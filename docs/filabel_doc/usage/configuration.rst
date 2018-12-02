Configuration
=============

Before you may start using :py:mod:`filabel`, it requires to be properly configured.

.. _github-conf-ref:

Github Configuration
--------------------

Communication with Github requires user authentication.
You will need to generate Github token and add to ``config/auth.cfg`` configuration file where this token will be retrieved for your communication.
Example::

   [github]
   token = <GITHUB_TOKEN>

WARNING: Be sure you keep your token private!


.. _label-conf-ref:

Label Configuration
-------------------

Let's look at how you configure, the relationship between labels and filenames.
In the configuration file `config/label.cfg`` you just define you wanted structure as shown on the example bellow.
Example::

    [labels]
        frontend=
            */templates/*
            static/*
        backend=
            logic/*
        docs=
            *.md
            LICENSE
            docs/*

Using this label configuration, all the pull requests containing any file from ``logic`` folder will be labeled as backend.
Pretty straight forward, right?


.. _webhook-conf-ref:

Webhook Configuration
---------------------

In the mode of web application, you need to add a webhook secret key to the same configuration file as a github token.
Example::

   [github]
   token = <GITHUB_TOKEN>
   secret = <WEBHOOK_SECRET_KEY>


The ``auth.cfg`` and ``label.cfg`` has to be stored in ``FILABEL_CONFIG`` enviroment variable for filabel to properly function.
Example::

    export FILABEL_CONFIG = "/path/to/auth.cfg:/path/to/label.cfg"

