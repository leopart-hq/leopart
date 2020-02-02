"""
Parser
====================================
The KiCad parser. The parser downloads the KiCad files that were previously saved to a pickle file by the crawler and
parses them using the realthunder kicad parser. It will create an sqlite database, that can then be searched by the
flask search app.
"""

import argparse
import logging
from configparser import ConfigParser
import pickle
import requests
import uuid
from libs.realthunder_kicad_parser import KicadPCB
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.exc import InterfaceError
from models.base import Base
from models.files import File
from models.repos import Repo
from models.items import Item
from models.part import Part
import os

# read the configuration
config = ConfigParser()
# Read config file path from environment variable in CI
try:
    print("READING ENV")
    env_config = os.environ['PARSER_CONFIG']
    config.read(env_config)
except KeyError:
    # No environment variable exists so we are not on GitLab
    config_path = 'config/parser.config'

    # check whether we have a config file
    if os.path.exists(config_path):
        config.read(config_path)
    else:
        print(f"Could not read config. Please check that the file is located in '{config_path}'.")
        exit(-3)
except Exception:
    print(f"Failed to initialize Configuration. Please check.")
    exit(-2)

# Check for db repo
db_path = config["DATABASE"]["database-uri"].split(":///")
if len(db_path) > 0:
    db_path = db_path[1]
    db_path = os.path.dirname(db_path)
    if not os.path.exists(db_path):
        os.mkdir(db_path)
else:
    print("Do not understand the db file config. Continuing nevertheless...")

# Init SQLAlchemy
engine = create_engine(config["DATABASE"]["database-uri"])
Base.metadata.create_all(engine)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("KiCad_Parser")
logger.setLevel(logging.DEBUG)

logfile_handler = logging.FileHandler(config["DEFAULT"]["Logfile"])
logfile_handler.setLevel(logging.DEBUG)

log_formatter = logging.Formatter("%(asctime)s [ 0] %(levelname)8s - %(name)15s  - %(message)s")
logfile_handler.setFormatter(log_formatter)

logger.addHandler(logfile_handler)


class RateLimitException(Exception):
    """
    Class for representing RateLimitException
    """

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


def parse_repos_from_pickle_file(pickle_file):
    """
    Parses a pickle file for repo and file information.

    :param pickle_file: picke file to parse
    :return: -
    """
    with open(pickle_file, "rb") as pf:
        list_of_repos = pickle.load(pf, encoding="UTF-8")

    num_of_repos = len(list_of_repos)
    repo_counter = 0

    for repo in list_of_repos:
        repo_counter += 1
        print(f"Currently parsing repo {repo_counter}/{num_of_repos}")
        logger.info(f"Fetching info for repo url: {repo['repo_url']}")

        session = Session()

        # TODO: Better to use one() and handle the exception
        repo_found = session.query(Repo).filter_by(repo_url=repo['repo_url']).first()

        if not repo_found:
            repo_new = Repo(repo_url=repo['repo_url'], repo_uuid=str(uuid.uuid4()),
                            description=repo['repo_description'],
                            name=repo['repo_name'], readme=repo['repo_readme'],
                            readme_url=repo['repo_readme_url'], license=repo['repo_license'],
                            license_url=repo['repo_license_url'], forks=int(repo['forks']),
                            stars=int(repo['stars']))

            # Save files and items in lists, only add to DB if all files of a repo have been parsed
            # as to not lose any in case we reach the rate limit

            list_of_results = []

            file = None
            items = None
            for file_url in repo['kicad_urls']:
                try:
                    file, items = parse_file_from_url(file_url)
                    list_of_results.append((file, items))
                except AssertionError:
                    logger.warning("File could not be parsed, skipping...")
                except TypeError:
                    logger.warning("File does not contain any modules, skipping...")
                except FileNotFoundError:
                    logger.warning("File can not be found anymore, skipping...")
                except ConnectionError as e:
                    logger.error(f"GitHub returned error: {e}")
                    raise e

            session.add(repo_new)
            session.commit()

            for file, list_of_items in list_of_results:
                # Skip if there was some error parsing the file
                if file is None:
                    continue

                file.repo_id = repo_new.id
                session.add(file)
                session.commit()

                for item in list_of_items:
                    item.file_id = file.id
                    session.add(item)
                    try:
                        session.commit()
                    except InterfaceError as e:
                        session.rollback()
                        logger.error(f"Could not insert item, probably due to a formatting error in the KiCad file. "
                                     f"Proceeding... Error message: {e}")

        else:
            logger.warning("Repository has already been parsed, skipping...")
        session.close()


def parse_file_from_url(file_url):
    """
    Parse a kicad file from a given URL.

    :param file_url: URL to fetch te file from
    :return: (files, items) touple. files represent information objects of files, and items vice versa.
    """
    session = Session()

    try:
        # TODO: Use one() with proper exceptions
        file = session.query(File).filter_by(url=file_url).first()

        # If we already have downloaded the file do not do anything
        if file:
            return None, None
        else:
            logger.info(f"Fetching file via url {file_url}...")
            resp = requests.get(url=file_url)

            logger.info(f"No uuid for file {file_url} yet found. Assigning one...")
            uid = str(uuid.uuid4())

            file = File(url=file_url, uuid=uid)

            if not resp.status_code == 200:
                if resp.status_code == 404:
                    logger.warning(f"File with url {file_url} could not be found, skipping...")
                    raise FileNotFoundError(f"File with URL {file_url} can not be found...")
                raise ConnectionError(f"Retrieval Exception. Cannot get data from {file_url}; status: "
                                      f"{resp.status_code}; message: {resp.text} ")

            logger.info("Fetching of file successful. Parsing to get included modules...")
            try:
                items = parse_kicad_file(resp.text)
            except IndexError as e:
                logger.error(f"Error parsing file, return none... Error message: {e}")
                return None, None
    except Exception as e:
        logger.error(f"Error checking if file has been parsed before: {e}")
        raise e
    finally:
        session.close()

    return file, items


def parse_kicad_file(contents):
    """
    Wrapper for reading pcb data out of text instead of file

    :param contents: file contents
    :return: item list
    """
    logger.info(f"Start Parsing of file.")
    pcb = KicadPCB.load_contents(contents)

    logger.info("Started extraction")

    if not hasattr(pcb, "module"):
        logger.warning("WARNING: the read file does not seem to contain any relevant data")
        return {}

    modules = []

    # Go through all modules in file
    for module in pcb.module:
        # Initialize. We need to do this as we would have problems later on (accessing the names would not be possible)
        desc = None
        tags = None
        reference = None
        value = None

        # try to extract description
        if hasattr(module, "descr"):
            desc = module["descr"]

        # try to extract tags
        if hasattr(module, "tags"):
            tags = module["tags"]

        # try to extract freetext fields
        if hasattr(module, "fp_text"):

            # iterate over freetext fields
            # Note: fp_text is part of KiCad for (free) text field in component
            for fp_text in module["fp_text"]:

                # if reference exists, save it
                if fp_text[0] == "reference":
                    reference = fp_text[1]

                # save value if it exists
                elif fp_text[0] == "value":
                    value = fp_text[1]

                else:
                    try:
                        logger.warning(f"Ignoring field '{fp_text[0]}' with value '{fp_text[1]}'")
                    except KeyError:
                        # fp_text[0] or fp_text[1] are empty, just continue...
                        pass
                    pass

        # save in data output
        modules.append({
            "module": module[0],
            "descr": desc,
            "tags": tags,
            "reference": reference,
            "value": value,
            "item_uuid": str(uuid.uuid4())
        })

    # remove duplicate entries
    modules = deduplicate(modules)

    # Remove common symbols
    modules = clean_data(modules)

    items = []
    if modules:
        for module in modules:
            # Create item with all info that we currently have
            item = Item(
                uuid=module["item_uuid"],
                module=module["module"],
                description=module["descr"],
                reference=module["reference"],
                tags=module["tags"],
                value=module["value"]
            )
            items.append(item)
    else:
        raise TypeError("Modules are empty!")
    logger.info("Extraction done for pcb...")

    return items


def clean_data(modules):
    """
    Removes the items by common symbols (names) like R for resistors etc...

    :param modules: the data to be cleaned
    :return: the cleaned data
    """
    # test if items are empty

    excluded_symbols = [
        r"R",  # Resistors
        r"D",  # Diode
        r"C",  # Capacitors
        r"L",  # Inductors
        r"F",  # Fuse
        r"P",  # pins
        r"S", r"SW",  # Switch
        r"TP",  # Test pads
        r"G",  # Graphics
        r"J",  # Jacks
        r"FID",  # Fiducial Markers (Reference Points)
        r"M",  # Mounting Holes/Points
        r"CON",  # Connectors
        r"REF",  # Reference points
        r"BT",  # Batteries
    ]

    common_components = [
        r"^\d*\.?\d*K$",  # Resistors
        r"^\d*\.?\d*M$",  # Resistors
        r"^\d*\.?\d*Mhz$",  # Crystals
        r"^conn_.*$",  # Connections
        r"^symbol_.*$",  # Something to be printed
        r"^resistor_.*$",  # Resistors
        r"^potentiometer_.*$",  # Potentiometers
        r"^gauge_.*$"  # Gauges
    ]

    common_comp_regex = "(" + ")|(".join(common_components) + ")"

    EXCLUDED_VALUES_FILE = "excluded_values.txt"
    if os.path.exists(EXCLUDED_VALUES_FILE):
        with open('excluded_values.txt', 'r') as f:
            excluded_values = f.read().splitlines()

    logger.debug("\t-> Removing by pattern...")

    if len(excluded_symbols) == 0:
        return modules

    # Build pattern
    pattern = r"^["
    for symbol in excluded_symbols:
        pattern += symbol.upper()
        pattern += symbol.lower()
    pattern += r"]{1,3}[\d:\*]+$"

    logger.debug(f"Exclude with pattern {pattern}")

    cleaned_modules = [module for module in modules if not re.match(pattern, module["reference"])
                       and not re.match(common_comp_regex, module['value'], re.IGNORECASE)]

    result = [module for module in cleaned_modules if
              isinstance(module["value"], str) and not module['value'].upper() in
              (value.upper() for value in excluded_values)]

    return result


def deduplicate(modules):
    """
    Removes duplicate extracted entries from modules list.

    :param modules: list of extracted modules to be cleaned.
    :return: module list w/o duplicates
    """
    logger.debug("\t-> Removing duplicates...")
    seen = []
    reduced = []

    for module in modules:
        if (module['module'], module['value']) not in seen:
            reduced.append(module)
            seen.append((module['module'], module['value']))

    return reduced


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Processes KiCAD files either from directotry, from a pickle file or '
                                                 'directly from the web.\n \n NOTE: Found Items will currently be '
                                                 'replaced after each found, so already found items are forgotten.')
    parser.add_argument('--pickle', "-p", type=str, nargs="?",
                        help='uses a pickle file')
    args = parser.parse_args()

    if args.pickle is None and args.kicad is None and args.url is None:
        print("Error: you need to at least specify one source (pickle)")
        exit()

    else:
        if args.pickle is not None:
            try:
                parse_repos_from_pickle_file(args.pickle)
            except RateLimitException:
                logger.warning("Stopping parser since the ratelimit for today has been reached...")
                exit(0)
