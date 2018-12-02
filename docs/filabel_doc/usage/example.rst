Example
=======

Github
------

.. testsetup::

    import os
    from filabel.logic import GitHub

    try:
        token = os.environ['GH_TOKEN']
    except:
        assert False, 'Set GH_TOKEN environment variable'

    github = GitHub(token)

    user = github.user()

First we need valid Github token in environment variable ``GH_TOKEN``.

.. testcode::

    from filabel.logic import GitHub

    github = GitHub(token)

    user = github.user()

    print('user: {}'.format(user["login"]))

.. testoutput::

    user: zvadaadam

.. testcode::

    labels = ['IS', 'IT', 'WORTH', 'IT', '?', 'NOT']

    repo = 'filabel-testrepo2'

    labels = github.reset_labels(user['login'], repo, 2, labels)

    print(labels[5]['name'])

.. testoutput::

    NOT

.. testcleanup::


    labels = github.reset_labels(user['login'], repo, 2, [])


Filabel
-------

.. testsetup::

    import os
    import configparser
    from filabel.logic import GitHub
    from filabel.logic import Filabel
    from filabel.utils import parse_labels

    try:
        token = os.environ['GH_TOKEN']
    except:
        assert False, 'Set GH_TOKEN environment variable'

    github = GitHub(token)
    username = github.user()['login']

    repo = '/filabel-testrepo4'

    ABS_PATH = os.getcwd()

    config_label = '/fixture/labels.example.cfg'
    config_paser = configparser.ConfigParser()
    config_paser.read('/Users/adamzvada/Documents/School/MI/MI-PYT/filabel-0-2.3/docs' + config_label)
    labels = parse_labels(config_paser)

    filabel = Filabel(token=token, labels=labels, state='open', base=None, delete_old=True, github=github)


First we need valid Github token in environment variable ``GH_TOKEN`` and path to label config file.

.. testcode::

    from filabel.logic import Filabel

    reposlug = f'{username}/{repo}'

    report = filabel.run_repo(reposlug)

    print(report.ok)

.. testoutput::

    True

.. testcleanup::

    github.reset_labels(username, repo, 2, [])
    github.reset_labels(username, repo, 3, [])