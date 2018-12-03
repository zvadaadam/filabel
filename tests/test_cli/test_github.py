import requests
import pytest
from filabel.logic import GitHub



REPO = 'filabel-testrepo2'


@pytest.mark.parametrize(
    ['repo', 'pr_length'],
    [('filabel-testrepo1', 0),
     ('filabel-testrepo2', 53),
     ('filabel-testrepo4', 2)],
)
def test_all_pr(username, repo, pr_length, github):

    pr = github.pull_requests(username, repo)

    if pr == []:
        my_pr_len = 0
    else:
        my_pr_len = len(pr)

    assert my_pr_len == pr_length


def test_invalid_repo(username, github):

    invalid_repo = 'WTF_REPO_42_FOO'

    with pytest.raises(requests.exceptions.HTTPError) as err:
        pr = github.pull_requests(username, invalid_repo)

    assert err


def test_user(username, github):

    user = github.user()

    assert username == user['login']


def test_pr_file(username, github):

    pr_file = github.pr_filenames(username, REPO, 1)

    print(pr_file)

    assert 'radioactive' in pr_file


def test_reset_labels(username, github):

    labels = ['CRAZY', 'MI-PYT']
    pr_index = 2

    prs = github.pull_requests(username, REPO)

    pr_labels = prs[pr_index]['labels']
    prev_labels = list(map(lambda x: x, pr_labels))

    labels = github.reset_labels(username, REPO, pr_index, labels)

    assert 'CRAZY' == labels[0]['name']
    assert 'MI-PYT' == labels[1]['name']

    github.reset_labels(username, REPO, pr_index, prev_labels)





