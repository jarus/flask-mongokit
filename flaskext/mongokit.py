# -*- coding: utf-8 -*-
"""
    flaskext.mongokit
    ~~~~~~~~~~~~~~~~~

    Make the integration of :mod:`mongokit` simpler into :mod:`Flask`.
    
    :copyright: 2011 by Christoph Heer <Christoph.Heer@googlemail.com
    :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

from mongokit import Connection, Database, Document
from flask import _request_ctx_stack

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

        app.before_request(self.open_connection)
        if hasattr(app, 'teardown_request'):
            app.teardown_request(self.close_connection)
        else:
            app.after_request(self.close_connection)
    
        # register extension with app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['mongokit'] = self
        
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
        return ctx.mongokit_db
     
    def disconnect(self):
        ctx = _request_ctx_stack.top
        ctx.mongokit_connection.disconnect()
       
    def open_connection(self):
        return self.connect()
        
    def close_connection(self, request):
        self.disconnect()
        return request