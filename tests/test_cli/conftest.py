import os
import betamax
import pytest

from betamax_serializers import pretty_json

from filabel.logic import GitHub


ABS_PATH = os.path.abspath(os.path.dirname(__file__))
CASSETTES_PATH = ABS_PATH + '/fixtures/cassettes'
CONFIGS_PATH = ABS_PATH + '/fixtures/configs'


with betamax.Betamax.configure() as config:

    config.CASSETTE_LIBRARY_DIR = CASSETTES_PATH
    config.default_cassette_options['serialize_with'] = 'prettyjson'

    token = os.environ.get('GITHUB_TOKEN', '<TOKEN>')

    if 'GITHUB_TOKEN' in os.environ:
        config.default_cassette_options['record_mode'] = 'once'
    else:
        config.default_cassette_options['record_mode'] = 'none'

    config.define_cassette_placeholder('<TOKEN>', token)



@pytest.fixture
def github(betamax_session):

    token = os.environ.get('GITHUB_TOKEN', '<TOKEN>')

    github = GitHub(token, betamax_session)

    return github