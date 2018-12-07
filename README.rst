filabel
=======

.. image:: https://travis-ci.com/zvadaadam/filabel-tests.svg?token=hQ9pHGbqJt1vNKYxDgN7&branch=master
    :target: https://travis-ci.com/zvadaadam/filabel-tests

|license| |pypi|

Tool for labeling PRs at GitHub by globs

Installation
------------

You can install this app in a standard way using ``setup.py``:

::

    $ python setup.py install
    $ pip install -e .

Or from PyPI:

::

    $ pip install filabel_cvut


Usage
-----

Run the CLI application simply with command and get to know it via help:

::

    $ filabel --help


Or run the web service

::

    $ export FILABEL_CONFIG=/path/to/my_labels.cfg:/path/to/my_auth.cfg
    $ export FLASK_APP=filabel
    $ flask run


For more info about configuration files, take a look at the content of
``config`` directory.


Documantation
____________

Documanation is created using Sphinx, before you build it you need to install this dependency.
::
    pip install -r docs/requirements.txt

To create the documentation, use following command
::
    make html

Tests
_____

Filabel unit test are running using Betamax with pregenerated cassettes on default username ``zvadaadam``.

Starting the unit tests is done by running
::
    $ python setup.py test


In order to run your own Filabel unit tests, you need generate your own cassettes and create the testing environment structure.

First, you will need to configure environment variables for GitHub authentication:
* ``GH_USER`` - GitHub username
* ``GH_TOKEN`` - GitHub access token with privileges to create repository and read the PRs

And the tests are running on explicit repository and pull requests structure so you need to run script which prepares the testing environment.
::
    $ ./test_environment/setup.sh


License
-------

This project is licensed under the MIT License - see the `LICENSE`_ file for more details.

.. _LICENSE: LICENSE


.. |license| image:: https://img.shields.io/github/license/cvut/filabel.svg
    :alt: License
    :target: LICENSE
.. |pypi| image:: https://badge.fury.io/py/filabel_cvut.svg
    :alt: PyPi Version
    :target: https://badge.fury.io/py/filabel_cvut
