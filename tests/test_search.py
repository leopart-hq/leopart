"""
This file supplies tests for the Search connector component.
"""
import json
import search
from models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

test_engine = create_engine('sqlite:///./database/parser_database.testing.sqlite')
Base.metadata.create_all(test_engine)
test_session = sessionmaker(bind=test_engine)
test_session = test_session()


def test_search_for_demo_out():
    """
    Testing if search performs as expected on a given known database
    """

    result = search.search("DEMO123", session=test_session)

    print("asdfasdöfasdfs\n\n", result)

    expected_result = (
        '{"status": "OK", "results": [{"repo_id": 1, "repo_name": "RepoName", "repo_desc": "A test repo", '
        '"repo_license": "RepoLic", "repo_license_url": "http://github.com/license", "repo_readme": "Readme", '
        '"repo_stars": 20, "repo_forks": 111, "repo_url": "https://github.com/testrepo", "files": [{"description": '
        '"Test Desc Item", "file_name": "test1.md", "file_url": "http://github.com/test1.md", "component": '
        '"DEMO1234", "tags": ["ItemTag"], "mpn": "STM32ASDF", "manufacturer": "TestMFG", "part_description": '
        '"Testpart", "datasheet": "http://www.yageo.com/documents/recent/PYu-RC_Group_51_RoHS_L_10.pdf"}, '
        '{"description": "Test Desc 2", "file_name": "test2.md", "file_url": "http://github.com/test2.md", '
        '"component": "DEMO1234", "tags": ["ItemTag"], "mpn": "STM32ASDF", "manufacturer": "TestMFG", '
        '"part_description": "Testpart", "datasheet": '
        '"http://www.yageo.com/documents/recent/PYu-RC_Group_51_RoHS_L_10.pdf"}, {"description": "Test Desc 3", '
        '"file_name": "test1.md", "file_url": "http://github.com/test1.md", "component": "DEMO123", '
        '"tags": ["ItemTag"], "mpn": "", "manufacturer": "", "part_description": "", "datasheet": ""}], '
        '"tags": ["ItemTag"]}]}'
    )

    assert result == expected_result


def test_search_for_fail_on_wrong_input():
    """
    Testing if search does not crash when given invalid input (here int)
    """

    result = search.search(-1, session=test_session)

    print("Result is:\n", result)

    expected_result = json.dumps(
        {
            "status": "OK",
            "results": []
        }
    )

    print("Expected:\n", expected_result)

    assert result == expected_result


def test_search_for_fail_on_no_connection():
    """
    Testing search if does not crash if the database does not exist.
    """
    test_engine = create_engine('sqlite:///')
    Base.metadata.create_all(test_engine)
    test_session = sessionmaker(bind=test_engine)
    test_session = test_session()

    result = search.search("DEMO123", session=test_session)

    print("Result is:\n", result)

    expected_result = json.dumps(
        {
            "status": "OK",
            "results": []
        }
    )

    print("Expected:\n", expected_result)

    assert result == expected_result
