import os
import betamax
import pytest
import configparser

#from betamax_serializers import pretty_json

from filabel.logic import GitHub
from filabel.logic import Filabel
from filabel.web import create_app

from filabel.utils import parse_labels


ABS_PATH = os.path.abspath(os.path.dirname(__file__))
CASSETTES_PATH = ABS_PATH + '/fixtures/cassettes'
CONFIGS_PATH = ABS_PATH + '/fixtures/configs'


with betamax.Betamax.configure() as config:

    config.cassette_library_dir = CASSETTES_PATH
    #config.default_cassette_options['serialize_with'] = 'prettyjson'
    config.default_cassette_options['match_requests_on'] = [
        'method',
        'uri',
    ]

    token = os.environ.get('GH_TOKEN', '<TOKEN>')

    if 'GH_TOKEN' in os.environ:
        config.default_cassette_options['record_mode'] = 'all'
    else:
        config.default_cassette_options['record_mode'] = 'none'

    config.define_cassette_placeholder('<TOKEN>', token)



@pytest.fixture
def github(betamax_session):

    token = os.environ.get('GH_TOKEN', '<TOKEN>')

    github = GitHub(token, betamax_session)

    return github


@pytest.fixture
def filabel(betamax_session):

    token = os.environ.get('GH_TOKEN', '<TOKEN>')

    github = GitHub(token, betamax_session)

    config_paser = configparser.ConfigParser()
    config_paser.read(CONFIGS_PATH + '/labels.abc.cfg')
    labels = parse_labels(config_paser)

    filabel = Filabel(token=token, labels=labels, state='open', base=None, delete_old=True, github=github)

    return filabel


# @pytest.fixture
# def test_app(betamax_session, github):
#
#     os.environ["FILABEL_CONFIG"] = CONFIGS_PATH + "/labels.abc.cfg"
#
#     test_app = create_app(github=github)
#
#
#     return test_app

