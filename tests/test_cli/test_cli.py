import os
import filabel

from click.testing import CliRunner

ABS_PATH = os.path.abspath(os.path.dirname(__file__))

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(filabel.cli, ['--help'])
    assert result.exit_code == 0
    assert 'CLI tool for filename-pattern-based labeling of GitHub PRs' in result.output


def test_cli_config_not_supplied():
    runner = CliRunner()

    config_auth = ABS_PATH + '/fixtures/configs/auth.fff.cfg'

    result = runner.invoke(filabel.cli, ['--config-auth', config_auth])

    assert 'Labels configuration not supplied' in result.output

def test_cli_invalid_value():
    runner = CliRunner()
    result = runner.invoke(filabel.cli, ['--config-labels', 'test'])

    assert result.exit_code == 2
    assert 'Invalid value' in result.output

def test_cli_reposlug_not_valid():
    runner = CliRunner()
    config_labels = ABS_PATH + '/fixtures/configs/labels.abc.cfg'
    config_auth = ABS_PATH +  '/fixtures/configs/auth.fff.cfg'
    slug = 'foobar'

    result = runner.invoke(filabel.cli, ['--config-labels', config_labels, '--config-auth', config_auth, slug])
    # assert result.exit_code == 2
    assert 'Reposlug {} not valid'.format(slug) in result.output

