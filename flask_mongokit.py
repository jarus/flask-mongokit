# -*- coding: utf-8 -*-
"""
    flaskext.mongokit
    ~~~~~~~~~~~~~~~~~

    Flask-MongoKit simplifies to use MongoKit, a powerful MongoDB ORM in Flask      
    applications. 
       
    :copyright: 2011 by Christoph Heer <Christoph.Heer@googlemail.com
    :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

import bson
from mongokit import Connection, Database, Document, Collection
from flask import _request_ctx_stack, abort
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
    :class:`~flaskext.mongokit.MongoKit` with keyword :attr:`ObjectId`.
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
        :meth:`~flaskext.mongokit.Document.find_one` but if there no document
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
        
        Also it registers the :class:`flaskext.mongokit.BSONObjectIdConverter`
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
        if hasattr(app, 'teardown_request'):
            app.teardown_request(self.teardown_request)
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
        
        :param documents: A :class:`list` of :class:`mongokit.Document`.
        """
        for document in documents:
            if document not in self.registered_documents:
                self.registered_documents.append(document)
        return self.registered_documents
    
    def connect(self):
        """Connect to the MongoDB server and register the documents from
        :attr:`registered_documents`. If you set ``MONGODB_USERNAME`` and
        ``MONGODB_PASSWORD`` then you will be authenticated at the
        ``MONGODB_DATABASE``.
        """
        ctx = _request_ctx_stack.top
        ctx.mongokit_connection = Connection(
            host=self.app.config.get('MONGODB_HOST'),
            port=self.app.config.get('MONGODB_PORT'),
            slave_okay=self.app.config.get('MONGODB_SLAVE_OKAY')
        )
        ctx.mongokit_connection.register(self.registered_documents)
        ctx.mongokit_db = Database(ctx.mongokit_connection,
                                   self.app.config.get('MONGODB_DATABASE'))
        if self.app.config.get('MONGODB_USERNAME') is not None:
            ctx.mongokit_db.authenticate(
                self.app.config.get('MONGODB_USERNAME'),
                self.app.config.get('MONGODB_PASSWORD')
            )
   
    @property
    def connected(self):
        """Connection status to your MongoDB."""
        ctx = _request_ctx_stack.top
        return hasattr(ctx, 'mongokit_db')
        
    def disconnect(self):
        """Close the connection to your MongoDB."""
        ctx = _request_ctx_stack.top
        if self.connected:
            ctx.mongokit_connection.disconnect()
            del ctx.mongokit_db
        
    def before_request(self):
        if not self.connected:
            self.connect()
        
    def teardown_request(self, request):
        self.disconnect()
        return request

    def __getattr__(self, func, **kwargs):
        if not self.connected:
            self.connect()
        ctx = _request_ctx_stack.top
        return getattr(ctx.mongokit_db, func)