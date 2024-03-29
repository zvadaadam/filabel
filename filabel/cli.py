import configparser
import click

from filabel.logic import Filabel, Change
from filabel.utils import parse_labels


def stylize_label_change(change_type, label):
    """
    Stylize change with given type and changed label

    :param change_type: type of change

    :param label: name of changed label

    :rtype:

    :return:
    """
    if change_type == Change.ADD:
        return click.style(f'+ {label}', fg='green')
    if change_type == Change.DELETE:
        return click.style(f'- {label}', fg='red')
    return f'= {label}'


def print_report_async(report):
    """
    Print Filabel report to command line in async mode

    :param report: Report to be printed
    """
    click.secho(f'REPO', nl=False, bold=True)
    click.secho(f' {report.repo} - ', nl=False)
    if report.ok:
        click.secho('OK', fg='green', bold=True)
        for pr_link, result in report.prs.items():
            click.secho(f'PR', nl=False, bold=True)
            click.secho(f' {pr_link} - ', nl=False)
            if result is None:
                click.secho('FAIL', fg='red', bold=True)
            else:
                click.secho('OK', fg='green', bold=True)
                for label, t in result:
                    click.echo(f'  {stylize_label_change(t, label)}')
    else:
        click.secho('FAIL', fg='red', bold=True)

def print_report(report):
    """
    Print Filabel report to command line

    :param report: Report to be printed
    """
    click.secho(f'REPO', nl=False, bold=True)
    click.secho(f' {report.repo} - ', nl=False)
    if report.ok:
        click.secho('OK', fg='green', bold=True)
        for pr_link, result in report.prs.items():
            click.secho(f'  PR', nl=False, bold=True)
            click.secho(f' {pr_link} - ', nl=False)
            if result is None:
                click.secho('FAIL', fg='red', bold=True)
            else:
                click.secho('OK', fg='green', bold=True)
                for label, t in result:
                    click.echo(f'    {stylize_label_change(t, label)}')
    else:
        click.secho('FAIL', fg='red', bold=True)


def get_token(config_auth):
    """
    Extract token from auth config and do the checks

    :param config_auth: ConfigParser with loaded configuration of auth
    """
    if config_auth is None:
        click.secho('Auth configuration not supplied!', err=True)
        exit(1)
    try:
        cfg_auth = configparser.ConfigParser()
        cfg_auth.read_file(config_auth)
        return cfg_auth.get('github', 'token')
    except Exception:
        click.secho('Auth configuration not usable!', err=True)
        exit(1)


def get_labels(config_labels):
    """
    Extract labels from labels config and do the checks

    :param config_labels: ConfigParser with loaded configuration of labels
    """
    if config_labels is None:
        click.secho('Labels configuration not supplied!', err=True)
        exit(1)
    try:
        cfg_labels = configparser.ConfigParser()
        cfg_labels.read_file(config_labels)
        return parse_labels(cfg_labels)
    except Exception:
        click.secho('Labels configuration not usable!', err=True)
        exit(1)


@click.command('filabel')
@click.option('-s', '--state', type=click.Choice(['open', 'closed', 'all']), default='open', show_default=True, help='Filter pulls by state.')
@click.option('-d/-D', '--delete-old/--no-delete-old', default=True, show_default=True, help='Delete labels that do not match anymore.')
@click.option('-b', '--base', type=str, metavar='BRANCH', help='Filter pulls by base (PR target) branch name.')
@click.option('-a', '--config-auth', type=click.File('r'), help='File with authorization configuration.')
@click.option('-l', '--config-labels', type=click.File('r'), help='File with labels configuration.')
@click.option('-x', '--async', 'async_run',is_flag=True, help='Using asyncio.')
@click.argument('reposlugs', nargs=-1)
def cli(reposlugs, state, delete_old, base, config_auth, config_labels, async_run):
    """
    CLI tool for filename-pattern-based labeling of GitHub Pull Requests (PRs).



    """
    token = get_token(config_auth)
    labels = get_labels(config_labels)
    check_reposlugs(reposlugs)

    fl = Filabel(token, labels, state, base, delete_old, async_run)

    reports = fl.run_repos(reposlugs)

    for report in reports:
        if async_run:
            print_report_async(report)
        else:
            print_report(report)

    # if fl.async_run:
    #     fl.async_run_repo(repo)
    # else:
    #
    # # make it async for reposlugs
    # for repo in reposlugs:
    #     report = fl.run_repo(repo)
    #     print_report(report)


def check_reposlugs(reposlugs):
    """
    Check formatting of reposlugs (contains 1 "/")

    :param list[str] reposlugs: List of reposlugs (i.e. "owner/repo")
    """
    for reposlug in reposlugs:
        if len(reposlug.split('/')) != 2:
            click.secho(f'Reposlug {reposlug} not valid!', err=True)
            exit(1)
