Usage
=====

Filabel can be used as a command line to or like a web application.

CLI
---

Example of basic usage in command line.
Example::

    $ python filabel -a auth.cfg -l label.cfg MI-PYT/consumes-a-lot-of-time

This command will run Filabel with your defined configuration file ``auth.cfg`` and label structure ``label.cfg`` on repository ``MI-PYT/consumes-a-lot-of-time``.

For advanced documentation for command line parameters, check documentation ....

Web application
---------------

Web application you run as a Flask project because Filabel is build on it.

Example::

    $ export FLASK_APP=filabel
    $ python flask run

