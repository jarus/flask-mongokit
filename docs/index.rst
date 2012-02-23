==============
Flask-MongoKit
==============
.. currentmodule:: flask.ext.mongokit

Flask-MongoKit simplifies to use `MongoKit`_, a powerful `MongoDB`_ ORM 
in Flask applications. If you find bugs or want to support this extension you can find the source code `here`_.

.. _MongoKit: http://namlook.github.com/mongokit/
.. _MongoDB: http://www.mongodb.org/
.. _here: http://bitbucket.org/Jarus/flask-mongokit/

Installation
============
The installation is thanks to the Python Package Index and `pip`_ really simple.

.. code-block:: console

   $ pip install Flask-MongoKit

If you only can use `easy_install` than use

.. code-block:: console

   $ easy_install Flask-MongoKit

.. _pip: http://pip.openplans.org/

Flask-MongoKit requires to run some packages (they will be installed automatically if they not already installed):

* Flask
* MongoKit
* pymongo

Your first Document
===================
It is very simple to use MongoKit in your Flask application. Let's create a simple ToDo application.

.. code-block:: python

    from datetime import datetime

    from flask import Flask, request, render_template, redirect, url_for
    from flask.ext.mongokit import MongoKit, Document

    app = Flask(__name__)

    class Task(Document):
        __collection__ = 'tasks'
        structure = {
            'title': unicode,
            'text': unicode,
            'creation': datetime,
        }
        required_fields = ['title', 'creation']
        default_values = {'creation': datetime.utcnow}
        use_dot_notation = True 

    db = MongoKit(app)
    db.register([Task])

As you can see we create a document model as class *Task* which uses Document from flask.ext.mongokit as parent class. In this model we describe the structure of our document and we can set a list of required fields and default values. The :class:`flask.ext.mongokit.Document` is beside some extensions the same like :class:`mongokit.Document` so if you want to know more about the core features of the Document class please look into the `MongoKit documentation`_. For using the the document model we must register it with the connection. But we use the :meth:`~flask.ext.mongokit.MongoKit.register` method from the :class:`flask.ext.mongokit.MongoKit` class.

Now we need a view to add a new task like this.

.. code-block:: python
    
    @app.route('/new', methods=["GET", "POST"])
    def new_task():
        if request.method == 'POST':
            task = db.Task()
            task.title = request.form['title']
            task.text = request.form['text']
            task.save()
            return redirect(url_for('show_all'))
        return render_template('new.html')

If someone now clicks on the submit button of the form your application will create a new instance of your Task model class. After that we set title and text of the task and save it into your MongoDB.

But now we want to get a list of task, so we add an other view.

.. code-block:: python

    @app.route('/')
    def show_all():
        tasks = db.Task.find()
        return render_template('list.html', tasks=tasks)

This view is very simple. You can see we only call the :meth:`find` method and put the result into our template. Now we have a running example that works simple with a MongoDB inside a Flask application.

If you want to see a full example of Flask-MongoKit look inside the repository. You will find there this ToDo application with the matching templates.

.. _MongoKit documentation: http://namlook.github.com/mongokit/descriptors.html

Configuration values
--------------------

The following configuration variables are used in Flask-MongoKit:

.. tabularcolumns:: |p{6.5cm}|p{8.5cm}|

=============================== =========================================
``MONGODB_DATABASE``            The database name that should used.
                                
                                *Default value:* ``flask``
``MONGODB_HOST``                Hostname or IP address of the MongoDB host.

                                *Default value:* ``localhost``
``MONGODB_PORT``                Listening port of the MongoDB host.

                                *Default value:* ``27017``
``MONGODB_USERNAME``            If you need authentication than you can set             
                                there your username.

                                *Default value:* ``None``
``MONGODB_PASSWORD``            Password for authentication.

                                *Default value:* ``None``
=============================== =========================================

    
API Documentation
=================

.. autoclass:: MongoKit
    :members:

.. autoclass:: Document
    :members:

.. autoclass:: BSONObjectIdConverter
    :members:
