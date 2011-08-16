==============
Flask-MongoKit
==============
.. currentmodule:: flaskext.mongokit

Flask-MonogKit makes it easy to use `MongoKit`_, a powerful `MongoDB`_ ORM 
in Flask applications. 

.. _MongoKit: http://namlook.github.com/mongokit/
.. _MongoDB: http://www.mongodb.org/

Installation
============
The installation is thanks the Python Package Index and `pip`_ really simple.

.. code-block:: console

   $ pip install Flask-MongoKit

If you can only use `easy_install` than use

.. code-block:: console

   $ easy_install Flask-MongoKit

.. _pip: http://pip.openplans.org/

Flask-MongoKit requires to run some packages (they will be installed automated if they not already installed):

* Flask
* MongoKit
* pymongo

Your first Document
===================
It is very simple and fast to use MongoKit in your Flask application. Lets create a simple ToDo application

.. code-block:: python

    from datetime import datetime

    from flask import Flask, request, render_template, redirect, url_for
    from flaskext.mongokit import MongoKit, Document

    app = Flask(__name__)

    class Task(Document):
        __collection__ = 'tasks'
        structure = {
            'title': unicode,
            'text': unicode,
            'creation': datetime,
        }
        required_fields = ['title', 'creation']
        default_values = {'creation': datetime.utcnow()}
        use_dot_notation = True 

    db = MongoKit(app)
    db.register([Task])

You can see we create a model (class Task) for our document and definied a structur, a list of required fields and default values. Also we say that we want to use a dot notation. To learn more about the definition of a Document look into the `MongoKit documentation`_.

Now we want that we can add a task over a form into our database.

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
    
Now if someone click now on the form button we create a new instance of our model Task and set in the next two lines title and text. After that we save the object into your database and redirect the visitor to the list of all task.

.. code-block:: python

    @app.route('/')
    def show_all():
        tasks = db.Task.find()
        return render_template('list.html', tasks=tasks)

With the find method we get now a list of task which is going to show on the index page.

.. _MongoKit documentation: http://namlook.github.com/mongokit/descriptors.html

    
API Documentation
=================

.. autoclass:: MongoKit
    :members:
