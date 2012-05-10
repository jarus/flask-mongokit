# -*- coding: utf-8 -*-

import unittest
import os

from datetime import datetime

from flask import Flask
from flaskext.mongokit import MongoKit, BSONObjectIdConverter, \
                               Document, Collection
from werkzeug.exceptions import BadRequest, NotFound
from bson import ObjectId

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

class TestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['MONGODB_DATABASE'] = 'flask_testing'

        maybe_conf_file = os.path.join(os.getcwd(), "config_test.cfg")
        if os.path.exists(maybe_conf_file):
            self.app.config.from_pyfile(maybe_conf_file)

        self.db = MongoKit(self.app)

        self.ctx = self.app.test_request_context('/')
        self.ctx.push()
                    
    def tearDown(self):
        self.ctx.pop()
        
    def test_initialization(self):
        self.db.register([BlogPost])
        
        assert len(self.db.registered_documents) > 0
        assert self.db.registered_documents[0] == BlogPost
        
        assert isinstance(self.db, MongoKit)
        assert self.db.name == self.app.config['MONGODB_DATABASE']
        assert isinstance(self.db.test, Collection)

    def test_decorator_registration(self):
        
        @self.db.register
        class DecoratorRegistered(Document):
            pass

        assert len(self.db.registered_documents) > 0
        assert self.db.registered_documents[0] == DecoratorRegistered
    
    def test_property_connected(self):
        assert not self.db.connected

        self.db.connect()
        assert self.db.connected
        
        self.db.disconnect()
        assert not self.db.connected
        
    def test_bson_object_id_converter(self):
        converter = BSONObjectIdConverter("/")
        
        self.assertRaises(BadRequest, converter.to_python, ("132"))
        assert converter.to_python("4e4ac5cfffc84958fa1f45fb") == \
               ObjectId("4e4ac5cfffc84958fa1f45fb")
        assert converter.to_url(ObjectId("4e4ac5cfffc84958fa1f45fb")) == \
               "4e4ac5cfffc84958fa1f45fb"
        
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

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCase))
    return suite
        
if __name__ == '__main__':
    unittest.main()        
