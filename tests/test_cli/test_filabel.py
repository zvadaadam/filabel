import pytest
import betamax

from filabel.logic import Report
from filabel.logic import Change

REPO = 'filabel-testrepo4'

def test_run_pr(username, filabel, github):

    pr = github.pull_requests(username, REPO)

    labels = filabel.run_pr(username, REPO, pr[0])

    assert len(labels) == 2 and labels[0][0] == 'ab'


def test_run_repo(username, filabel, github, betamax_session):

    reposlug = f'{username}/{REPO}'

    github.reset_labels(username, REPO, 2, [])
    github.reset_labels(username, REPO, 3, [])

    report = filabel.run_repo(reposlug)

    assert report.ok == True
    assert report.repo == reposlug
    assert report.prs['https://github.com/zvadaadam/filabel-testrepo4/pull/3'][0][0] == 'ab'
    assert report.prs['https://github.com/zvadaadam/filabel-testrepo4/pull/3'][1][1] == Change.ADD
    assert report.prs['https://github.com/zvadaadam/filabel-testrepo4/pull/2'][2][1] == Change.ADD


def test_matching_labels(username, filabel_param, github):

    filenames = ['static/foo_dynamic', 'logic/ddddd', 'aaaaa']

    labels = filabel_param._matching_labels(filenames)

    act_labels = filabel_param.labels

    if 'frontend' in act_labels:
        assert 'frontend' in labels
        assert 'backend' in labels
    else:
        assert 'a' in labels
        assert 'ab' in labels
        assert 'abc' in labels