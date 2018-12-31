import enum
import fnmatch
import itertools
import requests
import aiohttp
import asyncio
import abc
import configparser
from urllib import parse
from filabel.utils import parse_labels


class PaginationStrategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def paginated_get(self, url, params=None, headers=None, session=None):
        pass


class SyncPagination(PaginationStrategy):

    def paginated_get(self, url, params=None, headers=None, session=None):
        """"
        If the request response can be paginated, it retrives the whole response.

        :raise HTTPError: if during the request is raised

        :param url: url for outgoing request

        :param Optinal[dict[str, str] params: parameters for request

        :rtype dict: json

        :return: whole already paginated json reponse for given url and params
        """

        r = session.get(url, params=params)
        r.raise_for_status()
        json = r.json()

        if 'next' in r.links and 'url' in r.links['next']:
            json += self.paginated_get(r.links['next']['url'], params=params, session=session)

        return json


class AsyncPagination(PaginationStrategy):

    def paginated_get(self, url, params=None, headers=None, session=None):

        #loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        json = loop.run_until_complete(self._paginated_get(url, params=params, headers=headers))

        loop.close()

        return json

    async def _paginated_get(self, url, params=None, headers=None, session=None):

        #print('PAGINATED ASYNC')

        session = aiohttp.ClientSession(headers=headers, raise_for_status=True)
        async with session:
            future = asyncio.ensure_future(self._get_reponse(session, url, params))

            json, links = await future

            if links != None:
                next_num = self._page_num_from_ulr(links[0]['url'])
                last_num = self._page_num_from_ulr(links[1]['url'])

                futures = [asyncio.ensure_future(
                    self._get_reponse(session, self._url_with_page_num(links[0]['url'], page_num)))
                        for page_num in range(next_num, last_num + 1)]

                reponse_paginated = await asyncio.gather(*futures)

                for reponse in reponse_paginated:
                    json += reponse[0]

            return json

    async def _get_reponse(self, session, url, params=None):

        #print('async reponse')

        async with session.get(url, params=params) as response:

            future_json = await response.json()
            links = None
            if response.headers.get('Link'):
                links = requests.utils.parse_header_links(response.headers.get('Link'))

            return future_json, links

    def _url_with_page_num(self, url, num):

        parsed_url = parse.urlparse(url)

        url_dict = parse.parse_qs(parsed_url.query)
        url_dict['page'] = [num]

        parsed_url = list(parsed_url)

        parsed_url[4] = parse.urlencode(url_dict, doseq=True)

        return parse.urlunparse(parsed_url)



    def _page_num_from_ulr(self, url):

        parsed_url = parse.urlparse(url)

        return int(parse.parse_qs(parsed_url.query)['page'][0])


class GitHub:
    """
    GitHub API Wrapper, class for communication with the GitHub API with implementaed methods for purposes for Filabel,
    mainly focused on retriving and editing labels of pull requests etc..

    User needs to be authenticated with GitHub token, which is send in the request's header.
    """
    API = 'https://api.github.com'

    def __init__(self, token, strategy=None, session=None):
        """
        Initilizer for GitHub API wrapper.

        :param str token: GitHub token

        :param Optinal[session] session: optional requests session
        """

        self.strategy = strategy or SyncPagination()

        self.token = token
        self.session = session or requests.Session()
        self.session.headers = {'User-Agent': 'filabel'}
        self.session.auth = self._token_auth

    def _token_auth(self, req):
        """
        This alters all our outgoing requests by setting up the Github authentication token in the header request.

        :param req: outgoing requests

        :return: updated requests with GitHub token
        """
        req.headers['Authorization'] = 'token ' + self.token
        return req

    def auth_header(self):

        return {'User-Agent': 'Python' , 'Authorization': f'token {self.token}'}

    def user(self):
        """
        Get current Github user authenticated by given token

        :rtype dict: json

        :return: current user information
        """
        #return self._paginated_json_get(f'{self.API}/user')

        url = f'{self.API}/user'
        return self.strategy._paginated_get(url, headers=self.auth_header(), session=self.session)

    def pull_requests(self, owner, repo, state='open', base=None):
        """
        Get all Pull Requests of a defined repositary.

        :param str owner: GtiHub user or org

        :param str repo: repo name

        :param str state: defines the state for retrived PR
                          Default: open
                          Set of values: ["open", "closed", "all"]

        :param str base: optional branch the PRs are open for

        :rtype dict: json

        :return: all pull request for given defined repo
        """
        params = {'state': state}
        if base is not None:
            params['base'] = base
        url = f'{self.API}/repos/{owner}/{repo}/pulls'

        return self.strategy.paginated_get(url, params=params, headers=self.auth_header(), session=self.session)

    async def async_pull_requests(self, owner, repo, state='open', base=None):
        """
        Get all Pull Requests of a defined repositary.

        :param str owner: GtiHub user or org

        :param str repo: repo name

        :param str state: defines the state for retrived PR
                          Default: open
                          Set of values: ["open", "closed", "all"]

        :param str base: optional branch the PRs are open for

        :rtype dict: json

        :return: all pull request for given defined repo
        """
        params = {'state': state}
        if base is not None:
            params['base'] = base
        url = f'{self.API}/repos/{owner}/{repo}/pulls'

        return await self.strategy._paginated_get(url, params=params, headers=self.auth_header(), session=self.session)

    def pr_files(self, owner, repo, number):
        """
        Get files request for one defined Pull Request by ID

        :param str owner: Github username

        :param str repo: name of the repository

        :param int number: ID of the PR

        :rtype dict: json

        :return: changed filenames for one given PR
        """
        url = f'{self.API}/repos/{owner}/{repo}/pulls/{number}/files'

        return self.strategy.paginated_get(url, headers=self.auth_header(), session=self.session)

    async def async_pr_files(self, owner, repo, number):
        """
        Get files request for one defined Pull Request by ID

        :param str owner: Github username

        :param str repo: name of the repository

        :param int number: ID of the PR

        :rtype dict: json

        :return: changed filenames for one given PR
        """
        url = f'{self.API}/repos/{owner}/{repo}/pulls/{number}/files'

        return await self.strategy._paginated_get(url, headers=self.auth_header(), session=self.session)

    def pr_filenames(self, owner, repo, number):
        """
        Get just the filename for one Pull Request, a generator.

        :param str owner: Github username

        :param str repo: name of the repository

        :param int number: ID of the PR

        :rtype dict: json

        :return: changed filenames for one given PR
        """
        return (f['filename'] for f in self.pr_files(owner, repo, number))

    async def async_pr_filenames(self, owner, repo, number):
        """
        Get just the filename for one Pull Request, a generator.

        :param str owner: Github username

        :param str repo: name of the repository

        :param int number: ID of the PR

        :rtype dict: json

        :return: changed filenames for one given PR
        """
        return (f['filename'] for f in await self.async_pr_files(owner, repo, number))

    def reset_labels(self, owner, repo, number, labels):
        """
        Set's labels for Pull Request by replacing all the existing lables.

        :param str owner: Github username

        :param str repo: name of the repository

        :param int number: ID of the PR

        :param list[str] lables: all lables this PR will have

        :rtype dict: json

        :return: new labels for the pull request
        """
        url = f'{self.API}/repos/{owner}/{repo}/issues/{number}'
        r = self.session.patch(url, json={'labels': labels})
        r.raise_for_status()
        return r.json()['labels']


class Change(enum.Enum):
    """
    Enumeration of possible label changes
    Set of values: [ADD=1, DELETE=2, NONE=3]
    """
    ADD = 1
    DELETE = 2
    NONE = 3


class Report:
    """
    Simple container for reporting repo-pr label changes
    """
    def __init__(self, repo):
        """
        Initilizer for Report class.

        :param str repo: name of repository
        """
        self.repo = repo
        self.ok = True
        self.prs = {}


class Filabel:
    """
    Filabel tool labeling defined pull requests.

    We provide a configuration which files should be labeled and Filabel tool do the rest.
    """
    def __init__(self, token, labels, state='open', base=None, delete_old=True, async_run=False, github=None):
        """
        Initilizer for Filabel class.

        :param str token: GitHub token

        :param list[str] labels: Configuration of labels with globs

        :param str state: State of PR to be (re)labeled

        :param str base: Base branch of PRs to be (re)labeled

        :param delete_old: If no longer matching labels should be deleted

        :param Optional[Github] github: inilized Github API wrapper
        """

        if async_run:
            self.github = github or GitHub(token, strategy=AsyncPagination())
        else:
            self.github = github or GitHub(token, strategy=SyncPagination())

        self.labels = labels
        self.state = state
        self.base = base
        self.delete_old = delete_old
        self.async_run = async_run

    @property
    def defined_labels(self):
        """
        Set of labels defined in configuration

        :rtype: set[str]

        :return: labels by given configuration
        """
        return set(self.labels.keys())

    def _matching_labels(self, pr_filenames):
        """
        Find matching labels based on given filenames with used configuration label file

        :param list[str] pr_filenames: list of filenames as strings

        :rtype: set[str]

        :return: used labels in PR filenames
        """
        labels = set()
        for filename in pr_filenames:
            for label, patterns in self.labels.items():
                for pattern in patterns:
                    if fnmatch.fnmatch(filename, pattern):
                        labels.add(label)
                        break
        return labels

    def _compute_labels(self, defined, matching, existing):
        """
        Compute added, remained, deleted, and future label sets

        :param list[str] defined: Set of defined labels in config

        :param set[str] matching: Set of matching labels that should be in PR

        :param set[str] existing: Set of labels that are currently in PR

        :rtype: tuple(set[str], set[str], set[str], set[str])

        :return: Tuple of
        """
        added = matching - existing
        remained = matching & existing
        deleted = set()
        future = existing
        if self.delete_old:
            deleted = (existing & defined) - matching
            future = existing - defined
        future = future | matching
        return added, remained, deleted, future

    def run_pr(self, owner, repo, pr_dict):
        """
        Manage labels for single given PR

        :param str owner: Owner of GitHub repository

        :param str repo: Name of GitHub repository

        :param dict pr_dict: PR as dict from GitHub API

        :rtypeprint :

        :return:
        """
        pr_filenames = list(
            self.github.pr_filenames(owner, repo, pr_dict['number'])
        )
        added, remained, deleted, future = self._compute_labels(
            self.defined_labels,
            self._matching_labels(pr_filenames),
            set(l['name'] for l in pr_dict['labels'])
        )

        new_labels = self.github.reset_labels(
            owner, repo, pr_dict['number'], list(future)
        )

        new_label_names = set(l['name'] for l in new_labels)
        return sorted(itertools.chain(
            [(a, Change.ADD) for a in added],
            [(r, Change.NONE) for r in remained],
            [(d, Change.DELETE) for d in deleted]
        )) if future == new_label_names else None

    async def async_run_pr(self, owner, repo, pr_dict):
        """
        Manage labels for single given PR

        :param str owner: Owner of GitHub repository

        :param str repo: Name of GitHub repository

        :param dict pr_dict: PR as dict from GitHub API

        :rtype :

        :return:
        """

        pr_filenames = list(await self.github.async_pr_filenames(owner, repo, pr_dict['number']))

        added, remained, deleted, future = self._compute_labels(
            self.defined_labels,
            self._matching_labels(pr_filenames),
            set(l['name'] for l in pr_dict['labels'])
        )

        new_labels = self.github.reset_labels(owner, repo, pr_dict['number'], list(future))

        new_label_names = set(l['name'] for l in new_labels)

        return sorted(itertools.chain(
            [(a, Change.ADD) for a in added],
            [(r, Change.NONE) for r in remained],
            [(d, Change.DELETE) for d in deleted]
        )) if future == new_label_names else None

    def run_repo(self, reposlug):
        """
        Manage labels for all matching PRs in given repo

        :param str reposlug: Reposlug (full name) of GitHub repo (i.e. "owner/name")

        :rtype :

        :return:
        """
        report = Report(reposlug)
        owner, repo = reposlug.split('/')
        try:
            prs = self.github.pull_requests(owner, repo, self.state, self.base)
        except Exception:
            report.ok = False
            return report

        # make async for prs
        for pr_dict in prs:
            url = pr_dict.get('html_url', 'unknown')
            report.prs[url] = None
            try:
                report.prs[url] = self.run_pr(owner, repo, pr_dict)
            except Exception:
                pass

        return report


    async def _run_repo(self, reposlug):
        """
        Manage labels for all matching PRs in given repo

        :param str reposlug: Reposlug (full name) of GitHub repo (i.e. "owner/name")

        :rtype :

        :return:
        """
        report = Report(reposlug)
        owner, repo = reposlug.split('/')
        try:
            prs = await self.github.async_pull_requests(owner, repo, self.state, self.base)
        except Exception as e:
            report.ok = False
            return report

        # make async for prs
        prs_report = await asyncio.gather(*[self.async_run_pr(owner, repo, pr_dict) for pr_dict in prs], return_exceptions=True)


        for pr_report, pr_dict in zip(prs_report, prs):
            url = pr_dict.get('html_url', 'unknown')
            if not isinstance(pr_report, requests.HTTPError):
                report.prs[url] = pr_report
            else:
                report.prs[url] = None


        return report

    def run_repos(self, reposlugs):

        if self.async_run:
            reports = self.async_run_repos(reposlugs)
        else:
            reports = self.sync_run_repos(reposlugs)

        return reports

    def async_run_repos(self, reposlugs):

        loop = asyncio.get_event_loop()

        reports = loop.run_until_complete(asyncio.gather(*[self._run_repo(reposlug=reposlug) for reposlug in reposlugs]))

        loop.close()

        return reports


    def sync_run_repos(self, reposlugs):

        reports = []
        for reposlug in reposlugs:
            reports.append(self.run_repo(reposlug))

        return reports



if __name__ == "__main__":

    import os
    import datetime

    os.environ['PYTHONASYNCIODEBUG'] = '1'
    token = os.environ.get('GH_TOKEN', '5de9bc5acb78c45e6e80c52a683400be1b3c2932')
    print(token)

    github = GitHub(token, strategy=AsyncPagination())
    #github = GitHub(token)

    owner = 'zvadaadam'
    repo = 'filabel-testrepo1'


    #CONFIGS_PATH = '/Users/adamzvada/D#ocuments/School/MI/MI-PYT/filabel-0-2.3/config/labels.test.cfg'
    CONFIGS_PATH = '/Users/adamzvada/Documents/School/MI/MI-PYT/filabel-0-2.3/tests/test/fixtures/labels.empty.cfg'
    config_paser = configparser.ConfigParser()
    config_paser.read(CONFIGS_PATH)
    labels = parse_labels(config_paser)
    filabel = Filabel(token=token, labels=labels, state='open', base=None, delete_old=True, github=github, async_run=True)
    #reposlugs = [f'{owner}/{repo}', f'{owner}/filabel-testrepo3']
    #reposlugs = ['hroncok/non-exsiting-repo', 'MarekSuchanek/non-exsiting-repo']
    reposlugs = ['hroncok/filabel-testrepo-everybody']

    from filabel.cli import print_report_async

    now = datetime.datetime.now()
    reports = filabel.run_repos(reposlugs)
    after = datetime.datetime.now()
    print(after - now)


    print(reports)

    for report in reports:
        print_report_async(report)








