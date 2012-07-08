# -*- coding: utf-8 -*-

import unittest
import os

from datetime import datetime

from flask import Flask
from flask_mongokit import MongoKit, BSONObjectIdConverter, \
                           Document, Collection, AuthenticationIncorrect
from werkzeug.exceptions import BadRequest, NotFound
from bson import ObjectId
from pymongo import Connection
from pymongo.collection import Collection

class BlogPost(Document):
    __collection__ = "posts"
    structure = {
        'title': unicode,
        'body': unicode,
        'author': unicode,
        'date_creation': datetime,
        'rank': int,
        'tags': [unicode],
    }
    required_fields = ['title', 'author', 'date_creation']
    default_values = {'rank': 0, 'date_creation': datetime.utcnow}
    use_dot_notation = True

def create_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['MONGODB_DATABASE'] = 'flask_testing'
    
    maybe_conf_file = os.path.join(os.getcwd(), "config_test.cfg")
    if os.path.exists(maybe_conf_file):
        app.config.from_pyfile(maybe_conf_file)
    
    return app

class TestCaseContextIndependent(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.db = MongoKit(self.app)

    def tearDown(self):
        pass
    
    def test_register_document(self):
        self.db.register([BlogPost])
        
        assert len(self.db.registered_documents) > 0
        assert self.db.registered_documents[0] == BlogPost
    
    def test_bson_object_id_converter(self):
        converter = BSONObjectIdConverter("/")
    
        self.assertRaises(BadRequest, converter.to_python, ("132"))
        assert converter.to_python("4e4ac5cfffc84958fa1f45fb") == \
               ObjectId("4e4ac5cfffc84958fa1f45fb")
        assert converter.to_url(ObjectId("4e4ac5cfffc84958fa1f45fb")) == \
               "4e4ac5cfffc84958fa1f45fb"

    def test_is_extension_registerd(self):
        assert hasattr(self.app, 'extensions')
        assert 'mongokit' in self.app.extensions
        assert self.app.extensions['mongokit'] == self.db

class BaseTestCaseInitAppWithContext():
    def setUp(self):
        self.app = create_app()

    def test_init_later(self):
        self.db = MongoKit()
        self.assertRaises(RuntimeError, self.db.connect)

        self.db.init_app(self.app)
        self.db.connect()
        assert self.db.connected

    def test_init_immediately(self):
        self.db = MongoKit(self.app)
        self.db.connect()
        assert self.db.connected

class BaseTestCaseWithContext():

    def test_initialization(self):
        assert isinstance(self.db, MongoKit)
        assert self.db.name == self.app.config['MONGODB_DATABASE']
        assert isinstance(self.db.test, Collection)

    def test_property_connected(self):
        assert not self.db.connected

        self.db.connect()
        assert self.db.connected

        self.db.disconnect()
        assert not self.db.connected
        
        self.db.collection_names()
        assert self.db.connected
    
    def test_subscriptable(self):
        assert isinstance(self.db['test'], Collection)
        assert self.db['test'] == self.db.test

    def test_save_and_find_document(self):
        self.db.register([BlogPost])

        assert len(self.db.registered_documents) > 0
        assert self.db.registered_documents[0] == BlogPost

        post = self.db.BlogPost()
        post.title = u"Flask-MongoKit"
        post.body = u"Flask-MongoKit is a layer between Flask and MongoKit"
        post.author = u"Christoph Heer"
        post.save()

        assert self.db.BlogPost.find().count() > 0
        rec_post = self.db.BlogPost.find_one({'title': u"Flask-MongoKit"})
        assert rec_post.title == post.title
        assert rec_post.body == rec_post.body
        assert rec_post.author == rec_post.author

    def test_get_or_404(self):
        self.db.register([BlogPost])

        assert len(self.db.registered_documents) > 0
        assert self.db.registered_documents[0] == BlogPost

        post = self.db.BlogPost()
        post.title = u"Flask-MongoKit"
        post.body = u"Flask-MongoKit is a layer between Flask and MongoKit"
        post.author = u"Christoph Heer"
        post.save()

        assert self.db.BlogPost.find().count() > 0
        assert "get_or_404" in dir(self.db.BlogPost)
        try:
            self.db.BlogPost.get_or_404(post['_id'])
        except NotFound:
            self.fail("There should be a document with this id")
        self.assertRaises(NotFound, self.db.BlogPost.get_or_404, ObjectId())

    def test_find_one_or_404(self):
        self.db.register([BlogPost])

        assert len(self.db.registered_documents) > 0
        assert self.db.registered_documents[0] == BlogPost

        post = self.db.BlogPost()
        post.title = u"Flask-MongoKit"
        post.body = u"Flask-MongoKit is a layer between Flask and MongoKit"
        post.author = u"Christoph Heer"
        post.save()

        assert self.db.BlogPost.find().count() > 0
        assert "find_one_or_404" in dir(self.db.BlogPost)
        try:
            self.db.BlogPost.find_one_or_404({'title': u'Flask-MongoKit'})
        except NotFound:
            self.fail("There should be a document with this title")
        self.assertRaises(NotFound, self.db.BlogPost.find_one_or_404,
                          {'title': u'Flask is great'})

class BaseTestCaseWithAuth():
    def setUp(self):
        db = 'flask_testing_auth'
        conn = Connection()
        conn[db].add_user('test', 'test')
        
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['MONGODB_DATABASE'] = db
        
        self.db = MongoKit(self.app)

    def test_correct_login(self):
        self.app.config['MONGODB_USERNAME'] = 'test'
        self.app.config['MONGODB_PASSWORD'] = 'test'
        
        self.db.connect()
    
    def test_incorrect_login(self):
        self.app.config['MONGODB_USERNAME'] = 'fuu'
        self.app.config['MONGODB_PASSWORD'] = 'baa'
        
        self.assertRaises(AuthenticationIncorrect, self.db.connect)

class BaseTestCaseMultipleApps():

    def setUp(self):
        self.app_1 = create_app()
        self.app_1.config['MONGODB_DATABASE'] = 'app_1'
        
        self.app_2 = create_app()
        self.app_2.config['MONGODB_DATABASE'] = 'app_2'
        
        assert self.app_1 != self.app_2
        
        self.db = MongoKit()
        self.db.init_app(self.app_1)
        self.db.init_app(self.app_2)

    def tearDown(self):
        self.pop_ctx()

    def push_ctx(self):
        raise NotImplementedError
    
    def pop_ctx(self):
        raise NotImplementedError

    def test_app_1(self):
        self.push_ctx(self.app_1)
        
        self.db.connect()
        assert self.db.connected
        assert self.db.name == 'app_1'
        assert self.db.name != 'app_2'
        
    def test_app_2(self):
        self.push_ctx(self.app_2)
        
        self.db.connect()
        assert self.db.connected
        assert self.db.name != 'app_1'
        assert self.db.name == 'app_2'

class TestCaseInitAppWithRequestContext(BaseTestCaseInitAppWithContext, unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        
        self.ctx = self.app.test_request_context('/')
        self.ctx.push()
        
    def tearDown(self):
        self.ctx.pop()

class TestCaseWithRequestContext(BaseTestCaseWithContext, unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.db = MongoKit(self.app)
    
        self.ctx = self.app.test_request_context('/')
        self.ctx.push()
    
    def tearDown(self):
        self.ctx.pop()

class TestCaseWithRequestContextAuth(BaseTestCaseWithAuth, unittest.TestCase):
    def setUp(self):
        super(TestCaseWithRequestContextAuth, self).setUp()
        
        self.ctx = self.app.test_request_context('/')
        self.ctx.push()
    
    def tearDown(self):
        self.ctx.pop()

class TestCaseMultipleAppsWithRequestContext(BaseTestCaseMultipleApps, unittest.TestCase):
    def push_ctx(self, app):
        self.ctx = app.test_request_context('/')
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

# Only testing is the flask version support app context (since flask v0.9)
if hasattr(Flask, "app_context"):
    class TestCaseInitAppWithAppContext(BaseTestCaseInitAppWithContext, unittest.TestCase):
        def setUp(self):
            self.app = create_app()
    
            self.ctx = self.app.app_context()
            self.ctx.push()
    
        def tearDown(self):
            self.ctx.pop()
    
    class TestCaseWithAppContext(BaseTestCaseWithContext, unittest.TestCase):
        def setUp(self):
            self.app = create_app()
            self.db = MongoKit(self.app)
            
            self.ctx = self.app.app_context()
            self.ctx.push()
        
        def tearDown(self):
            self.ctx.pop()
    
    class TestCaseWithAppContextAuth(BaseTestCaseWithAuth, unittest.TestCase):
        def setUp(self):
            super(TestCaseWithAppContextAuth, self).setUp()
    
            self.ctx = self.app.app_context()
            self.ctx.push()
    
        def tearDown(self):
            self.ctx.pop()
    
    class TestCaseMultipleAppsWithAppContext(BaseTestCaseMultipleApps, unittest.TestCase):
        def push_ctx(self, app):
            self.ctx = app.app_context()
            self.ctx.push()
         
        def tearDown(self):
            self.ctx.pop()

if __name__ == '__main__':
    unittest.main()
