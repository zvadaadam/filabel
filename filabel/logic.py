import enum
import fnmatch
import itertools
import requests
import aiohttp
import asyncio
from urllib import parse



class GitHub:
    """
    GitHub API Wrapper, class for communication with the GitHub API with implementaed methods for purposes for Filabel,
    mainly focused on retriving and editing labels of pull requests etc..

    User needs to be authenticated with GitHub token, which is send in the request's header.
    """
    API = 'https://api.github.com'

    def __init__(self, token, session=None):
        """
        Initilizer for GitHub API wrapper.

        :param str token: GitHub token

        :param Optinal[session] session: optional requests session
        """
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

    def async_session(self):

        return aiohttp.ClientSession(headers={'User-Agent': 'filabel', 'Authorization': f'token {self.token}'})

    async def _paginated_json_get_async(self, url, params=None):
        """
        """

        session = self.async_session()
        async with session:
            future = asyncio.ensure_future(self._get_reponse(session, url, params))

            json, links = await future

            if links != None:
                next_num = self.page_num_from_ulr(links[0]['url'])
                last_num = self.page_num_from_ulr(links[1]['url'])

                reponse_paginated = await asyncio.gather(*[self._get_reponse(session, self.url_with_page_num(links[0]['url'], page_num)) for page_num in range(next_num, last_num + 1)])

                for reponse in reponse_paginated:
                    json += reponse[0]

            return json

            #reponse_paginated = await asyncio.gather(*[self._get_reponse(session, url) for url in links])

    def url_with_page_num(self, url, num):

        parsed_url = parse.urlparse(url)

        url_dict = parse.parse_qs(parsed_url.query)
        url_dict['page'] = [num]

        parsed_url = list(parsed_url)

        parsed_url[4] = parse.urlencode(url_dict, doseq=True)

        return parse.urlunparse(parsed_url)



    def page_num_from_ulr(self, url):
        """

        :param url:
        :return:
        """
        parsed_url = parse.urlparse(url)

        return int(parse.parse_qs(parsed_url.query)['page'][0])


    async def _get_reponse(self, session, url, params=None):
        """

        :param session:
        :param url:
        :param params:
        :return:
        """

        async with session.get(url, params=params) as response:

            future_json = await response.json()

            links = None
            if response.headers.get('Link'):
                links = requests.utils.parse_header_links(response.headers.get('Link'))

            return future_json, links



    def _paginated_json_get(self, url, params=None):

        """"
        If the request response can be paginated, it retrives the whole response.

        :raise HTTPError: if during the request is raised

        :param url: url for outgoing request

        :param Optinal[dict[str, str] params: parameters for request

        :rtype dict: json

        :return: whole already paginated json reponse for given url and params
        """

        r = self.session.get(url, params=params)
        r.raise_for_status()
        json = r.json()
        if 'next' in r.links and 'url' in r.links['next']:
            json += self._paginated_json_get(r.links['next']['url'], params)
        return json

    def user(self):
        """
        Get current Github user authenticated by given token

        :rtype dict: json

        :return: current user information
        """
        return self._paginated_json_get(f'{self.API}/user')

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

        #return self._paginated_json_get(url, params)

        loop = asyncio.get_event_loop()

        json = loop.run_until_complete(self._paginated_json_get_async(url, params))

        loop.close()

        return json


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

        #print(url)

        return self._paginated_json_get(url)

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
    def __init__(self, token, labels, state='open', base=None, delete_old=True, github=None):
        """
        Initilizer for Filabel class.

        :param str token: GitHub token

        :param list[str] labels: Configuration of labels with globs

        :param str state: State of PR to be (re)labeled

        :param str base: Base branch of PRs to be (re)labeled

        :param delete_old: If no longer matching labels should be deleted

        :param Optional[Github] github: inilized Github API wrapper
        """
        if github == None:
            self.github = GitHub(token)
        else:
            self.github = github

        self.labels = labels
        self.state = state
        self.base = base
        self.delete_old = delete_old

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

        :rtype :

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

        for pr_dict in prs:
            url = pr_dict.get('html_url', 'unknown')
            report.prs[url] = None
            try:
                report.prs[url] = self.run_pr(owner, repo, pr_dict)
            except Exception:
                pass
        return report


if __name__ == "__main__":

    import os

    os.environ['PYTHONASYNCIODEBUG'] = '1'
    token = os.environ.get('GH_TOKEN', 'edd303d73b09c5e6914b5c881ee4b6b6bd8ff398')
    print(token)

    github = GitHub(token)

    owner = 'zvadaadam'
    repo = 'filabel-testrepo2'

    pr = github.pull_requests(owner, repo)

    print(pr)

