========================
RDRHC Calendar Generator
========================

A specialized program to create an iCal file from a Microsoft Excel schedule.

Initial Setup (Development)
===========================

1. Install the virtual environment

.. code:: shell

  pipenv install --dev

2. Create the required config file - you may copy the example config
   located at ``/config/.rdrhc_calendar.cfg``.

3. Update the config file to specify all the required details (as
   outlined in the example config file.

Running Program
===============

.. code:: shell

  pipenv run python run.py path_to_config_file

Testing
=======

Unit tests for this application can be run via the standard pytest commands:

.. code:: shell

  # Standard testing
  pipenv run pytest

  # Tests with coverage reporting
  pipenv run pytest --cov=modules --cov-report=xml


All reports can be placed in the reports folder, whose contents are excluded
from source control.

Linting
=======

Linting for this application can be run with the following commands:

.. code:: shell

  # Linting via Pylint (Excluding Tests)
  $ pipenv run pylint run.py modules/

  # Linting via Pylint (Tests Only)
  $ pipenv run pylint tests/ --min-similarity-lines=20

  # Linting via Pycodestyle
  $ pipenv run pycodestyle run.py modules/ tests/
