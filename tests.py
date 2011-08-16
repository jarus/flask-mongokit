# -*- coding: utf-8 -*-

import unittest

from datetime import datetime

from flask import Flask
from flaskext.mongokit import MongoKit, Document

class BlogPost(Document):
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

class TestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        self.ctx = self.app.test_request_context()
        self.ctx.push()
                
    def tearDown(self):
        self.ctx.pop()
        
    def test_initialize(self):
        db = MongoKit(self.app)
        db.register([BlogPost])
        
        assert len(db.registered_documents) > 0
        assert db.registered_documents[0] == BlogPost
        
        db.connect()
        db.disconnect()
        
if __name__ == '__main__':
    unittest.main()        