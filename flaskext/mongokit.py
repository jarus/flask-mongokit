# -*- coding: utf-8 -*-
"""
    flaskext.mongokit
    ~~~~~~~~~~~~~~~~~

    Make the integration of :mod:`mongokit` simpler into :mod:`Flask`.
    
    :copyright: 2011 by Christoph Heer <Christoph.Heer@googlemail.com
    :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

import bson
from mongokit import Connection, Database, Document, Collection
from flask import _request_ctx_stack, abort
from werkzeug.routing import BaseConverter

class BSONObjectIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            return bson.ObjectId(value)
        except bson.errors.InvalidId, e:
            raise abort(400)
        
    def to_url(self, value):
        return str(value)

class MongoKit(object):
    
    def __init__(self, app=None):
        #: list of MongoKit.Document which will be automated registed at
        #: connection
        self.registered_documents = []
        
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
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
        
        app.url_map.converters['MongoDBObjectID'] = BSONObjectIDConverter
        
        self.app = app
    
    def register(self, documents):
        for document in documents:
            if document not in self.registered_documents:
                self.registered_documents.append(document)
        return self.registered_documents
    
    def connect(self):
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
        ctx = _request_ctx_stack.top
        return hasattr(ctx, 'mongokit_db')
        
    def disconnect(self):
        ctx = _request_ctx_stack.top
        if self.connected:
            ctx.mongokit_connection.disconnect()
        
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