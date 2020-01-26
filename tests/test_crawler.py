import crawler
import pickle
import os


def test_crawler():
    """Testing index route"""

    crawler.main(test=True)

    with open('repos_test.pickle', 'rb') as f:
        list_of_repos = pickle.load(f)

        assert len(list_of_repos) > 0, 'No repo saved in pickle file!'
        assert list_of_repos[0]['repo_url'] != '', 'Repo URL empty!'
        assert list_of_repos[0]['repo_name'] != '', 'Repo Name empty!'
        assert list_of_repos[0]['stars'] != '', 'Repo has no stars!'
        assert list_of_repos[0]['forks'] != '', 'Repo has no forks!'

        # Teardown
        os.remove('repos_test.pickle')
