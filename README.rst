========================
RDRHC Calendar Generator
========================

A specialized program to create an iCal file from a Microsoft Excel schedule.

Initial Setup (Development)
===========================

1. Install the virtual environment

.. code:: shell

  pipenv install --dev

2. Create the required config file (should be located in a parent folder
named "config") - TODO: add demo config file.

Running Program
===============

.. code:: shell

  pipenv run python run.py path_to_application

Testing
=======

Unit tests for this application can be run via the standard pytest commands:

.. code:: shell

  # Standard testing
  pipenv run py.test tests/

  # Tests with coverage reporting
  pipenv run py.test --cov=modules --cov-report=xml tests/

  # Tests with JUnit reporting
  pipenv run py.test --junitxml=reports/tests.xml tests/

All reports can be placed in the reports folder, whose contents are excluded
from source control.
