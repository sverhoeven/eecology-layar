Layar web service for hosting track on http://www.uva-bits.nl/kml/visiting-amsterdam-for-a-day/

Getting Started
===============

Requirements
------------

Database with geoalchemy support.
See http://geoalchemy.org/

Install
-------

.. code-block:: bash

  cd <directory containing this file>
  python setup.py develop

Init db
-------

.. code-block:: bash

  wget http://www.uva-bits.nl/wp-content/uploads/2011/05/S355_museumplein.kmz
  unzip S355_museumplein.kmz
  initialize_eecology_layar_db development.ini S355_museumplein.kml

Start server
------------

.. code-block:: bash

  pserve development.ini

Layar
=====

1. Register as developer
2. Create layer
3. Set endpoint to server url
4. Setup icons, texts, coverage, etc.
