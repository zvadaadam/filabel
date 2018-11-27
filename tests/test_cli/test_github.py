import pytest
from filabel.logic import GitHub


@pytest.mark.parametrize()
def test_all_pr(github):

    owner = 'zvadaada'
    repo = 'test'

    pr = github.pull_requests(owner, repo)

    print(pr)

    assert pr != None