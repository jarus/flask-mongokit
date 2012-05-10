# -*- coding: utf-8 -*-
"""
    flask.ext.mongokit
    ~~~~~~~~~~~~~~~~~~

    Flask-MongoKit simplifies to use MongoKit, a powerful MongoDB ORM in Flask
    applications.

    :copyright: 2011 by Christoph Heer <Christoph.Heer@googlemail.com
    :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

import bson
from mongokit import Connection, Database, Collection, Document
from flask import abort
from werkzeug.routing import BaseConverter


class BSONObjectIdConverter(BaseConverter):
    """A simple converter for the RESTfull URL routing system of Flask.

    .. code-block:: python

        @app.route('/<ObjectId:task_id>')
        def show_task(task_id):
            task = db.Task.get_from_id(task_id)
            return render_template('task.html', task=task)

    It checks the validate of the id and converts it into a
    :class:`bson.objectid.ObjectId` object. The converter will be
    automatically registered by the initialization of
    :class:`~flask.ext.mongokit.MongoKit` with keyword :attr:`ObjectId`.
    """

    def to_python(self, value):
        try:
            return bson.ObjectId(value)
        except bson.errors.InvalidId:
            raise abort(400)

    def to_url(self, value):
        return str(value)


class Document(Document):
    def get_or_404(self, id):
        """This method get one document over the _id field. If there no
        document with this id then it will raised a 404 error.

        :param id: The id from the document. The most time there will be
                   an :class:`bson.objectid.ObjectId`.
        """
        doc = self.get_from_id(id)
        if doc is None:
            abort(404)
        else:
            return doc

    def find_one_or_404(self, *args, **kwargs):
        """This method get one document over normal query parameter like
        :meth:`~flask.ext.mongokit.Document.find_one` but if there no document
        then it will raise a 404 error.
        """

        doc = self.find_one(*args, **kwargs)
        if doc is None:
            abort(404)
        else:
            return doc


class MongoKit(object):
    """This class is used to integrate `MongoKit`_ into a Flask application.

    :param app: The Flask application will be bound to this MongoKit instance.
                If an app is not provided at initialization time than it
                must be provided later by calling :meth:`init_app` manually.

    .. _MongoKit: http://namlook.github.com/mongokit/
    """

    def __init__(self, app=None):
        #: :class:`list` of :class:`mongokit.Document`
        #: which will be automated registed at connection
        self.registered_documents = []
        self.mongokit_connection = None

        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        """This method sets up some :meth:`~flask.Flask.before_request` and
        :meth:`~flask.Flask.after_request` or
        :meth:`~flask.Flask.teardown_request` handlers to support that
        MongoKit opens a connection to your MongoDB host on a request and
        closes after the response.

        Also it registers the
        :class:`flask.ext.mongokit.BSONObjectIdConverter`
        as a converter with the key word **ObjectId**.

        :param app: The Flask application will be bound to this MongoKit
                    instance.
        """
        app.config.setdefault('MONGODB_HOST', '127.0.0.1')
        app.config.setdefault('MONGODB_PORT', 27017)
        app.config.setdefault('MONGODB_DATABASE', 'flask')
        app.config.setdefault('MONGODB_SLAVE_OKAY', False)
        app.config.setdefault('MONGODB_USERNAME', None)
        app.config.setdefault('MONGODB_PASSWORD', None)

        app.before_request(self.before_request)

        # 0.9 and later
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown_request)
        # 0.7 to 0.8
        elif hasattr(app, 'teardown_request'):
            app.teardown_request(self.teardown_request)
        # Older Flask versions
        else:
            app.after_request(self.teardown_request)

        # register extension with app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['mongokit'] = self

        app.url_map.converters['ObjectId'] = BSONObjectIdConverter

        self.app = app

    def register(self, documents):
        """Register one or more :class:`mongokit.Document` instances to the
        connection.

        Can be also used as a decorator on documents:

        .. code-block:: python

            db = MongoKit(app)

            @db.register
            class Task(Document):
                structure = {
                   'title': unicode,
                   'text': unicode,
                   'creation': datetime,
                }

        :param documents: A :class:`list` of :class:`mongokit.Document`.
        """

        #enable decorator usage as in mongokit.Connection
        decorator = None
        if not isinstance(documents, (list, tuple, set, frozenset)):
            # we assume that the user used this as a decorator
            # using @register syntax or using db.register(SomeDoc)
            # we stock the class object in order to return it later
            decorator = documents
            documents = [documents]

        for document in documents:
            if document not in self.registered_documents:
                self.registered_documents.append(document)

        if decorator is None:
            return self.registered_documents
        else:
            return decorator

    def connect(self):
        """Connect to the MongoDB server and register the documents from
        :attr:`registered_documents`. If you set ``MONGODB_USERNAME`` and
        ``MONGODB_PASSWORD`` then you will be authenticated at the
        ``MONGODB_DATABASE``.
        """
        self.mongokit_connection = Connection(
            host=self.app.config.get('MONGODB_HOST'),
            port=self.app.config.get('MONGODB_PORT'),
            slave_okay=self.app.config.get('MONGODB_SLAVE_OKAY')
        )
        self.mongokit_connection.register(self.registered_documents)
        self.mongokit_db = Database(self.mongokit_connection,
                                   self.app.config.get('MONGODB_DATABASE'))
        if self.app.config.get('MONGODB_USERNAME') is not None:
            self.mongokit_db.authenticate(
                self.app.config.get('MONGODB_USERNAME'),
                self.app.config.get('MONGODB_PASSWORD')
            )

    @property
    def connected(self):
        """Connection status to your MongoDB."""
        return self.mongokit_connection is not None

    def disconnect(self):
        """Close the connection to your MongoDB."""
        if self.connected:
            self.mongokit_connection.disconnect()
            self.mongokit_connection = None
            del self.mongokit_db

    def before_request(self):
        if not self.connected:
            self.connect()

    def teardown_request(self, request):
        self.disconnect()
        return request

    def __getattr__(self, name, **kwargs):
        if not self.connected:
            self.connect()
        return getattr(self.mongokit_db, name)
