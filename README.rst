Flask-MongoKit
==============

.. image:: https://secure.travis-ci.org/jarus/flask-mongokit.png
   :target: http://travis-ci.org/jarus/flask-mongokit

Flask-MongoKit simplifies to use `MongoKit`_, a powerful `MongoDB`_ ORM 
in Flask applications.

.. _MongoKit: http://namlook.github.com/mongokit/
.. _MongoDB: http://www.mongodb.org/
.. _here: http://bitbucket.org/Jarus/flask-mongokit/

Installation
------------
The installation is thanks to the Python Package Index and `pip`_ really simple.

::

   $ pip install Flask-MongoKit

If you only can use `easy_install` than use

::

   $ easy_install Flask-MongoKit

.. _pip: http://pip.openplans.org/

Flask-MongoKit requires to run some packages (they will be installed automatically if they not already installed):

* Flask
* MongoKit
* pymongo

Changes
-------

* **0.4**: Support new import system of flask. Use now:

::
   
   form flask.ext.mongokit import Mongokit
