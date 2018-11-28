import pytest
import betamax

from filabel.logic import Report
from filabel.logic import Change

OWNER = 'zvadaadam'
REPO = 'filabel-testrepo4'


def test_run_pr(filabel, github):

    pr = github.pull_requests(OWNER, REPO)

    labels = filabel.run_pr(OWNER, REPO, pr[1])

    assert len(labels) == 3 and labels[0][0] == 'a'


def test_run_repo(filabel, github, betamax_session):

    reposlug = f'{OWNER}/{REPO}'

    with betamax_session as vcr:
        vcr.use_cassette('tests/test_cli/fixtures/cassettes/tests.test_cli.test_github.test_all_pr.json')
        pr = github.pull_requests(OWNER, REPO)

    print(pr)

    for my_pr in pr:
        github.reset_labels(OWNER, REPO, my_pr['number'], [])

    report = filabel.run_repo(reposlug)

    for pr in report.prs:
        print(pr)

    assert report.ok == True
    assert report.repo == reposlug
    assert report.prs['https://github.com/zvadaadam/filabel-testrepo4/pull/3'][1][0] == 'abc'
    assert report.prs['https://github.com/zvadaadam/filabel-testrepo4/pull/3'][1][1] == Change.ADD
    assert report.prs['https://github.com/zvadaadam/filabel-testrepo4/pull/2'][2][1] == Change.ADD

