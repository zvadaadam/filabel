import os
import betamax
import pytest
import configparser

#from betamax_serializers import pretty_json

from filabel.logic import GitHub
from filabel.logic import Filabel
from filabel.web import create_app
from click.testing import CliRunner

from filabel.utils import parse_labels


ABS_PATH = os.path.abspath(os.path.dirname(__file__))
CASSETTES_PATH = ABS_PATH + '/fixtures/cassettes'
CONFIGS_PATH = ABS_PATH + '/fixtures/configs'

USER_DEFAULT = 'zvadaadam'


with betamax.Betamax.configure() as config:

    config.cassette_library_dir = CASSETTES_PATH
    #config.default_cassette_options['serialize_with'] = 'prettyjson'
    config.default_cassette_options['match_requests_on'] = [
        'method',
        'uri',
        'body',
        'headers',
        'path',
    ]

    token = os.environ.get('GH_TOKEN', '<TOKEN>')

    if 'GH_TOKEN' in os.environ:
        config.default_cassette_options['record_mode'] = 'all'
    else:
        config.default_cassette_options['record_mode'] = 'none'

    config.define_cassette_placeholder('<TOKEN>', token)



@pytest.fixture
def github(betamax_session):

    #token = os.environ.get('GH_TOKEN', '<TOKEN>')

    github = GitHub(token, betamax_session)

    return github


@pytest.fixture
def filabel(betamax_session, request):

    default_config = '/labels.abc.cfg'
    token = os.environ.get('GH_TOKEN', '<TOKEN>')

    github = GitHub(token, betamax_session)

    config_paser = configparser.ConfigParser()
    config_paser.read(CONFIGS_PATH + default_config)
    labels = parse_labels(config_paser)

    filabel = Filabel(token=token, labels=labels, state='open', base=None, delete_old=True, github=github)

    return filabel

@pytest.fixture(params=('/labels.abc.cfg', '/labels.example.cfg'))
def filabel_param(betamax_session, request):

    token = os.environ.get('GH_TOKEN', '<TOKEN>')

    github = GitHub(token, betamax_session)

    config_paser = configparser.ConfigParser()
    config_paser.read(CONFIGS_PATH + request.param)
    labels = parse_labels(config_paser)

    filabel = Filabel(token=token, labels=labels, state='open', base=None, delete_old=True, github=github)

    return filabel

@pytest.fixture
def username(betamax_session):

    user = os.environ.get('GH_USER')

    if user is None:
        user = USER_DEFAULT

    return user

@pytest.fixture
def runner(betamax_session):
    return CliRunner()


@pytest.fixture
def test_app(betamax_session, github):

    os.environ["FILABEL_CONFIG"] = CONFIGS_PATH + "/labels.abc.cfg" + ':' + CONFIGS_PATH + '/auth.fff.cfg'

    test_app = create_app(github=github)

    test_app.config['TESTING'] = True

    return test_app.test_client()

