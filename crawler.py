"""
Crawler
====================================
The GitHub crawler. This crawler searches GitHub for repositories that contain 'KiCad' or 'PCB' in their description or
readme, checks if they contain .kicad_pcb files, and saves repository metadata and the file urls so that they can later
be parsed by the parser module.
"""
from github import Github, GithubException
import pickle
import time
from dateutil import rrule
import datetime
import calendar
import logging.handlers
from configparser import ConfigParser
import os

config = ConfigParser()

# check whether we have a custom config file
if os.path.exists('config/crawler.config'):
    config.read('config/crawler.config')
else:
    config.read('config/default_crawler.config')

RATE_LIMIT_SAFETY = int(config['DEFAULT']['RATE_LIMIT_SAFETY'])
try:
    GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
except KeyError:
    GITHUB_TOKEN = config['GitHub']['Token']

abuse_count = 0

logger = logging.getLogger("Crawler")
# Logger has to have 'lowest' Level. Nothing underneath this level is logged.
logger.setLevel(logging.DEBUG)
filehandler = logging.handlers.RotatingFileHandler(config['DEFAULT']['Logfile'], maxBytes=1024000, backupCount=1)
filehandler.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
logger.addHandler(filehandler)
logger.addHandler(ch)


def main(test=False):
    """
    This will iterate over all repositories on GitHub which have KiCad or pcb in their readme files. It uses slicing
    over the creation date of the repository to circumvent GitHubs 1000 items per response limit.

    :param test: When set to True, the crawler will write a pickle file as soon as a repository containing KiCad
    files has been found. Used for testing.
    """
    # Maximum per page seems to be 100, but it doesn't hurt to set it higher
    g = Github(GITHUB_TOKEN, per_page=1000)

    try:
        with open('crawler_status.pickle', 'rb') as f:
            crawler_status = pickle.load(f)
            # Begin from next (first non-complete) month. We may be adding a day too much here, but that shouldn't
            # matter as we only use year and month
            start_date = datetime.datetime.strptime(
                crawler_status['last_month_completed'], '%Y-%m'
            ) + datetime.timedelta(days=31)
            num_of_repos = crawler_status['repos_searched']
            num_of_files = crawler_status['files_found']
            logger.warning(f"Found crawler status file. {crawler_status['repos_searched']} repos searched and "
                           f"{crawler_status['files_found']} files found so far. Resuming search from "
                           f"{start_date.strftime('%Y-%m')}.")
        with open('repos.pickle', 'rb') as f:
            list_of_repos = pickle.load(f)
    except IOError:
        logger.warning("No crawler status file found, beginning search from 2015-01.")
        start_date = datetime.datetime.strptime('2015-01-01', '%Y-%m-%d')
        list_of_repos = []
        num_of_repos = 0
        num_of_files = 0

    end_date = datetime.datetime.now()

    try:
        # TODO: This has to be made more intelligent so that we can reduce the timespan if we get more than 1000 results
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date):
            # Find out last day of month
            last_day = calendar.monthrange(dt.year, dt.month)

            logger.info(f'Crawling GitHub repositories between {dt.strftime("%Y-%m")}-01 and '
                        f'{dt.strftime("%Y-%m")}-{last_day[1]}')

            # Search repositories containing .kicad_pcb files
            repos = g.search_repositories(f'kicad OR pcb in:readme created:'
                                          f'{dt.strftime("%Y-%m")}-01..{dt.strftime("%Y-%m")}-{last_day[1]}')
            try:
                if repos.totalCount >= 1000:
                    logger.warning(f"Warning! More than 1000 results included for month {dt.strftime('%Y-%m')}. "
                                   f"We missed some repositories!")
            except Exception as e:
                logger.warning(f"Exception accessing totalCount: {e}")

            try:
                for repo in repos:
                    logger.debug(f"Found repository {repo.html_url}")
                    num_of_repos += 1

                    content_files = g.search_code(f'.kicad_pcb in:path repo:{repo.full_name}')

                    license_text = 'Could not find license.md in repository, please check for the license ' \
                                   'before using the contents of this repository for your project!'
                    license_url = ''

                    try:
                        license = repo.get_license()
                        license_text = license.decoded_content
                        license_url = license.download_url
                    except Exception as e:
                        logger.error(f'Exception accessing license: {e}')

                    list_of_kicad_files = []
                    try:
                        for cf in content_files:
                            check_rate_limit(g, rl_limit=RATE_LIMIT_SAFETY, num_of_repos=num_of_repos,
                                             num_of_files=num_of_files, dt=dt)
                            download_url = cf.download_url
                            if download_url.endswith('.kicad_pcb'):
                                list_of_kicad_files.append(download_url)
                                num_of_files += 1

                    except GithubException as e:
                        handle_github_exception(e)
                        pass

                    check_rate_limit(g, rl_limit=RATE_LIMIT_SAFETY, num_of_repos=num_of_repos,
                                     num_of_files=num_of_files, dt=dt)

                    if list_of_kicad_files:
                        additional_info = g.search_code(f'README.md OR LICENSE.md in:path repo:{repo.full_name}')
                        try:
                            readme = 'Could not find readme in repository'
                            readme_url = ''
                            license_text = 'Could not find license.md in repository, please check for the license ' \
                                           'before using the ontents of this repository for your project!'
                            license_url = ''

                            for file in additional_info:
                                check_rate_limit(g, rl_limit=RATE_LIMIT_SAFETY, num_of_repos=num_of_repos,
                                                 num_of_files=num_of_files, dt=dt)

                                if file.name.lower() == 'readme.md':
                                    readme = file.decoded_content.decode('utf-8')
                                    readme_url = file.download_url

                        except GithubException as e:
                            handle_github_exception(e)
                            readme = 'Could not find readme in repository'
                            readme_url = ''
                            pass

                        info_dict = {
                            'repo_url': repo.html_url,
                            'repo_name': repo.name,
                            'repo_description': repo.description,
                            'repo_readme': readme,
                            'repo_readme_url': readme_url,
                            'repo_license': license_text,
                            'repo_license_url': license_url,
                            'kicad_urls': list_of_kicad_files,
                            'stars': repo.stargazers_count,
                            'forks': repo.forks_count
                        }

                        list_of_repos.append(info_dict)

                        # Only save one repo for testing
                        if test:
                            with open('repos_test.pickle', 'wb') as f:
                                pickle.dump(list_of_repos, f, pickle.HIGHEST_PROTOCOL)
                            return

            except GithubException as e:
                handle_github_exception(e)
                pass

            logger.info(f"Reached the end of month {dt.strftime('%Y-%m')}. Saving data to repos.pickle and status to "
                        f"crawler_status.pickle. Restarting the crawler will resume from this position.")
            save_list_of_repos(list_of_repos, num_of_repos, num_of_files, dt)

        logger.info('Reached current date. Stopping and writing to file...')
        save_list_of_repos(list_of_repos, num_of_repos, num_of_files, dt)
    except KeyboardInterrupt:
        logger.warning("Received Keyboard interrupt, stopping...")


def check_rate_limit(g, rl_limit, num_of_repos, num_of_files, dt):
    """
    Checks the current rate limit at GitHub and pauses if necessary to not exhaust the ratelimit

    :param g: the GitHub object that contains meta info, e.g. rate limit, rate limit resettime
    :param rl_limit: Contains the rate limit safety margin (so we don't get blocked for abuse)
    :param num_of_repos: The number of repos that have been crawled so far
    :param num_of_files: The number of KiCad files that have been found so far
    :param dt: The month that is currently being crawled
    """
    rate_limit_remaining = g.rate_limiting[0]
    rate_limit_reset_time = g.rate_limiting_resettime
    logger.debug(f'Rate limit remaining: {rate_limit_remaining}')

    if rate_limit_remaining < rl_limit:
        logger.info(f"Rate limit is reached, pausing until rate limit is refreshed, which will be at "
                    f"{datetime.datetime.fromtimestamp(rate_limit_reset_time)}.")
        logger.info(f"Status: Searched {num_of_repos} repositories and found {num_of_files} .kicad_pcb files. "
                    f"Currently searching {dt.strftime('%Y-%m')}")
        update_status(num_of_repos, num_of_files, dt)
        logger.warning(f"Ratelimit pause until {datetime.datetime.fromtimestamp(rate_limit_reset_time + 5)}")
        time.sleep(rate_limit_reset_time - time.time() + 5)
    else:
        update_status(num_of_repos, num_of_files, dt)


def update_status(num_of_repos, num_of_files, dt):
    """
    Print logging output
    :param num_of_repos: The number of repos that have been crawled so far
    :param num_of_files: The number of KiCad files that have been found so far
    :param dt: The month that is currently being crawled
    """
    logger.debug(f"Repositories crawled: {num_of_repos}")
    logger.debug(f"KiCAD files found: {num_of_files}")
    logger.debug(f"Currently crawling {dt.strftime('%Y-%m')}")
    logger.info(f"Abuse limit count: {abuse_count}")


def save_list_of_repos(list_of_repos, num_of_repos, num_of_files, dt):
    """
    Save repositories and files that have been crawled, create a status dict so that the crawling can be continued if it
    is cancelled in the meantime. This method is only called at the end of each month-slice, to allow for easy
    continuation (just start with the next month)
    :param list_of_repos: A list of dictionaries that contain all the info that has been found (e.g. repo urls,
    KiCad file urls)
    :param num_of_repos: The number of repos that have been crawled so far
    :param num_of_files: The number of KiCad files that have been found so far
    :param dt: The month that is currently being crawled
    """
    logger.warning(f"Crawling finished for month {dt.strftime('%Y-%m')}")
    logger.warning(f"Repos crawled (total): {num_of_repos}. KiCad files found (total): {num_of_files}")
    with open('crawler_status.pickle', 'wb') as f:
        status_dict = {
            'last_month_completed': dt.strftime('%Y-%m'),
            'repos_searched': num_of_repos,
            'files_found': num_of_files
        }
        pickle.dump(status_dict, f, pickle.HIGHEST_PROTOCOL)

    with open('repos.pickle', 'wb') as f:
        pickle.dump(list_of_repos, f, pickle.HIGHEST_PROTOCOL)


def handle_github_exception(e):
    """
    Check if exception was thrown due to an abuse detection. If so, wait 5 minutes.
    :param e: The error message
    """
    logger.debug(f"GithubException: {e}")
    if e.data["message"].startswith("You have triggered an abuse detection mechanism."):
        global abuse_count
        abuse_count += 1
        logger.warning(f"Abuse rate limit pause until {datetime.datetime.fromtimestamp(time.time() + 300)}, "
                       f"abuse count: {abuse_count}")
        time.sleep(300)


if __name__ == "__main__":
    logger.warning("Begin crawling.")
    main()
