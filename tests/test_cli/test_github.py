import requests
import pytest
from filabel.logic import GitHub

OWNER = 'zvadaadam'
REPO = 'filabel-testrepo4'

def test_all_pr(github):

    pr = github.pull_requests(OWNER, REPO)

    assert len(pr) == 2


def test_invalid_repo(github):

    invalid_repo = 'WTF_REPO'

    with pytest.raises(requests.exceptions.HTTPError) as err:
        pr = github.pull_requests(OWNER, invalid_repo)

    assert err

def test_empty_pr(github):

    my_repo = 'speech-recognition'

    pr = github.pull_requests(OWNER, my_repo)

    assert len(pr) == 0


def test_user(github):

    user = github.user()

    assert user is not None


def test_pr_file(github):

    pr_file = github.pr_filenames(OWNER, REPO, 1)

    print(pr_file)

    assert 'aaaa' in pr_file


def test_reset_labels(github):

    labels = ['CRAZY', 'MI-PYT']

    labels = github.reset_labels(OWNER, REPO, 2, labels)

    print(labels)

    assert 'MI-PYT' == labels[1]['name']





