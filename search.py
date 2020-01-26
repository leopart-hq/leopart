import json
from models.items import Item
from models.files import File
from models.repos import Repo
from models.base import Base
from models.part import Part
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os.path

# Init SQLAlchemy
engine = create_engine('sqlite:///./database/parser_database.sqlite?check_same_thread=false')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def preprocess_query(query: str, split: str = None):
    """
    Preprocess query.

    :param split: splitting char(s) default None>Whitespace
    :param query: query string
    :return: list of processed query terms
    """
    query = str(query)  # Just to make sure its a string!
    query = query.upper()
    query_items = query.split(split)
    return query_items


def sort_by_relevance(repo_list):
    """
    Build display order.

    As of 2020-01-14 it sorts by number of forks and stars combined
    :param repo_list: repolist to sort
    :return: sorted repolist
    """
    repo_list.sort(key=lambda repo: repo['repo_forks'] + repo['repo_stars'], reverse=True)
    return repo_list


def build_repo_object(repo: Repo):
    """
    Builds internal object representation for repos

    :param repo: repository info (As Repo object)
    :return: repository object
    """
    result = {
        'repo_id': repo.id,
        'repo_name': repo.name,
        'repo_desc': repo.description,
        'repo_license': repo.license,
        'repo_license_url': repo.license_url,
        'repo_readme': repo.readme,
        'repo_stars': repo.stars,
        'repo_forks': repo.forks,
        'repo_url': repo.repo_url,
        'files': [],
        'tags': []
    }
    return result


def build_file_item_object(item: Item, file: File, part: Part = None):
    """
    Builds internal representation of items and files.

    :param item: item info
    :param file: file info
    :param part: part info (if avail)
    :return: internal representation of part/file
    """
    result = {
        'description': item.description,
        'file_name': os.path.basename(file.url),
        'file_url': file.url,
        'component': item.value
    }

    if item.tags is not None:
        if item.tags.startswith("\""):
            item.tags = item.tags[1:]

        if item.tags.endswith("\""):
            item.tags = item.tags[:-1]

        result.update(
            {
                'tags': item.tags.split(";"),
            }
        )
    else:
        result.update(
            {
                'tags': [],
            }
        )

    if part is not None:
        result.update(
            {
                'mpn': part.mpn,
                'manufacturer': part.manufacturer,
                'part_description': part.description,
                'datasheet': part.datasheet
            }
        )
    else:
        result.update(
            {
                'mpn': "",
                'manufacturer': "",
                'part_description': "",
                'datasheet': ""
            }
        )
    return result


def search(query: str, separator: str = None, session=session):
    """
    Interface for querying parts from the database.

    :param session: override for session
    :param separator: separator of items (e.g. ", "; default whitespaces)
    :param query: query string (e.g. "ASDF123 ASDF21")
    :return:
    """
    try:
        query_items = preprocess_query(query, split=separator)

        # for now limit to one item
        if len(query_items) > 0:
            query_items = query_items[0]
        else:
            return "[]"

        # Fetch items corresponding to the query
        item_results = (
            session.query(
                Item, File, Part  # Select info from Items, Files & Parts
            )
            .filter(Item.value.ilike(f"%{query_items}%"))  # Search for query str
            # .filter(Item.part_id == Part.id)  # search for MPN (depricated)
            .filter(File.id == Item.file_id)  # Select file info from Files table
            .join(Part, Item.part_id == Part.id, isouter=True)  # Join info about parts if avail.
            .all()  # fetch all results
        )

        # here all repos are saved
        repo_list = []

        # Update info for each item
        for item in item_results:
            # fetch ids of repos already visited
            saved_repo_ids = [str(repo['repo_id']) for repo in repo_list]

            # if we don't know the info, fetch from db
            if str(item.File.repo_id) not in saved_repo_ids:
                # query the repo info
                repo = session.query(Repo).filter(Repo.id == item.File.repo_id).one()

                # build repo repres.
                repo_obj = build_repo_object(repo)

                # append file info repr. to repo
                files_data = build_file_item_object(item.Item, item.File, item.Part)
                repo_obj["files"].append(files_data)

                repo_obj["tags"].extend(files_data["tags"])
                repo_obj["tags"] = list(set(repo_obj["tags"]))

                # save to list
                repo_list.append(repo_obj)
            else:
                # find the repo
                repo_obj = [repo for repo in repo_list if str(repo['repo_id']) == str(item.File.repo_id)]

                if len(repo_obj) <= 0:
                    raise Exception("Something went wrong.")
                else:
                    repo_obj = repo_obj[0]

                # find the corresponding index
                repo_index = repo_list.index(repo_obj)

                # pop from list
                repo_obj = repo_list.pop(repo_index)

                # update files in object
                files_data = build_file_item_object(item.Item, item.File, item.Part)
                repo_obj["files"].append(files_data)

                repo_obj["tags"].extend(files_data["tags"])
                repo_obj["tags"] = list(set(repo_obj["tags"]))

                # re-add to list
                repo_list.append(repo_obj)

        # sort by relevance
        result_dict = sort_by_relevance(repo_list)

        print("res: ", result_dict)

        return json.dumps(
            {
                "status": "OK",
                "results": result_dict
            }
        )
    except Exception as ex:
        return json.dumps(
            {
                "status": "ERROR",
                "info": f"{ex}",
                "trace": ex.args
            }
        )
    finally:
        session.close()


if __name__ == "__main__":
    print("Searching...")
    print("Result:", search("STM32"))
