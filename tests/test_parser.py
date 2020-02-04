import pytest
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser
from sqlalchemy import create_engine, select, MetaData, Table
import requests
import os
import kicad_parser as kp

config = ConfigParser()

# check whether we have a custom config file
if os.path.exists('config/parser.config'):
    config.read('config/parser.config')
else:
    config.read('config/default_parser.config')


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

# Init SQLAlchemy

Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData(bind=None)


# Test Suite for Read from Pickle File
# Mark key used: readPickleFile
# Command to run Test Cases for Test Suite 1
# Positive Test Cases: pytest -m readPickleFile_withCorrectParams tests/test_parser.py
# Negative Test Cases: pytest -m readPickleFile_withWrongParams tests/test_parser.py


@pytest.mark.readPickleFile_withCorrectParams
def test_read_from_file():
    """
    Test Case 1: Testing method with Correct Params
    """
    # Flag Variable as a Check declared to verify the assertion
    check = True
    # Call the method
    kp.parse_repos_from_pickle_file("repos.testing.pickle")

    # Query on the items table to verify does it contains data or not
    table = Table('items', metadata, autoload=True, autoload_with=engine)
    stmt = select([table])
    connection = engine.connect()

    # Results of the query will be stored in results varriable
    results = session.execute(stmt).fetchall()

    if results is None:
        check = False

    # if assertion is True then the test case will Pass
    assert check is True


@pytest.mark.readPickleFile_withWrongParams
def test_read_from_wrong_file_():
    """
    Test Case 2: Testing without passing parameters to the function
    """
    # Try to raise the TypeError
    # match will do the matching of the ouput from the function
    with pytest.raises(TypeError, match=".*missing 1*."):
        kp.parse_repos_from_pickle_file()


@pytest.mark.readPickleFile_withWrongParams
def test_read_from_file_with_NegativeParams():
    """
    Test Case 3: Testing with passing negative parameter to the function
    """
    # capture the output of the function by passing the negative number
    with pytest.raises(ValueError, match=".*negative*."):
        kp.parse_repos_from_pickle_file(-1)
    # assert if the the captured output contains the string "negative file descriptor"


@pytest.mark.readPickleFile_withWrongParams
def test_read_from_file_with_PositiveParams():
    """
    Test Case 4: Testing with positive parameter to the function
    """
    # capture the output of the function by passing the negative number
    with pytest.raises(EOFError, match=".*Ran out of input*."):
        kp.parse_repos_from_pickle_file(2)


# Test Suite for Read from URL
# Mark key used: readFromURL
# Command to run Test Cases for Test Suite 1
# Positive Test Cases: pytest -m readFromURL_withCorrectParams tests/test_parser.py
# Negative Test Cases: pytest -m readFromURL_withWrongParams tests/test_parser.py

# @pytest.mark.readFromURL_withCorrectParams
# def test_read_from_URL_with_correctURL():
#     check = True
#     """
#     Test Case 5: Testing with correct URL that is already parsed so it will return (None, None)
#     """
#     file, items = kp.parse_file_from_url(
#             "https://raw.githubusercontent.com/linklayer/"
#             "cantact-hw/470252258a3967e7cebbb9538b848d505ace40fe/cantact.kicad_pcb")
#     if file is not None:
#         check = False
#     if items is not None:
#         check = False
#     assert check


@pytest.mark.readFromURL_withCorrectParams
def test_read_from_URL_with_correctURL_NotParsed():
    check = True
    """
    Test Case 6: Testing with correct URL that is not parsed so it will return some data
    """
    file, items = kp.parse_file_from_url(
        "https://raw.githubusercontent.com/nqbit/kicad-boards/1f46d28da1f3cf233ee2c6cc3741c78919b21b2c"
        "/arduino_template/camera.kicad_pcb")

    if file is None:
        check = False
    if items is None:
        check = False
    assert check


@pytest.mark.readFromURL_withWrongParams
def test_read_from_URL_with_PositiveParams():
    """
    Test Case 7: Testing with positive parameter to the function
    """
    # capture the output of the function by passing the negative number
    with pytest.raises(Exception, match=".*Invalid URL*."):
        kp.parse_file_from_url(2)


@pytest.mark.readFromURL_withWrongParams
def test_read_from_URL_with_NegativeParams():
    """
    Test Case 8: Testing with Negative parameter to the function
    """
    # capture the output of the function by passing the negative number
    with pytest.raises(Exception, match=".*Invalid URL*."):
        kp.parse_file_from_url(-1)


@pytest.mark.readFromURL_withWrongParams
def test_read_from_URL_with_WrongURLParams():
    """
    Test Case 9: Testing with Negative parameter to the function
    """
    # capture the output of the function by passing the negative number
    with pytest.raises(TypeError, match=".*object is not subscriptable*."):
        kp.parse_file_from_url("https://www.google.com/")


# Test Suite for From File Contents
# Mark key used: fromFileContents
# Command to run Test Cases for Test Suite 1
# Positive Test Cases: pytest -m fromFileContents_withCorrectParams tests/test_parser.py
# Negative Test Cases: pytest -m fromFileContents_withWrongParams tests/test_parser.py


@pytest.mark.fromFileContents_withWrongParams
def test_from_file_contents_with_correctParams():
    """
    Test Case 10: Testing from file contents with correct parameters
    """
    # Flag Variable decalred
    check = True
    resp = requests.get(
        url='https://raw.githubusercontent.com/nqbit/kicad-boards/1f46d28da1f3cf233ee2c6cc3741c78919b21b2c/'
            'arduino_template/camera.kicad_pcb'
    )
    data = kp.parse_kicad_file(resp.text)

    # if Data extracted is none then the test fails
    if data is None:
        check = False
    assert check is True


@pytest.mark.fromFileCOntents_withWrongParams
def test_from_file_contents_with_emptyParameters():
    """
    Test Case 11: Testing from file Contents with no parameters
    """
    with pytest.raises(TypeError, match=".*missing 1*."):
        kp.parse_kicad_file()


@pytest.mark.fromFileContents_withWrongParams
def test_from_file_contents_with_emptyWrongParameters():
    """
    Test Case 12: Testing from file Contents with wrong url
    """
    check = True
    with pytest.raises(TypeError, match=".*object is not subscriptable*."):
        # corrupt url
        resp = requests.get(
            url='https://raw.githubusercontent.com/nqbit/kicad-boards/1f46d28da1f3cf233ee2c6cc3741c78919b21b2c/'
                'arduino_template/camera.kicad_pcb'
        )
        data = kp.parse_kicad_file("sdc")

        # if Data extracted is none then the test fails
        if data is None:
            check = False
        assert check is True
