from flask_mongokit import Document

def decorator_registration(self):

    @self.db.register
    class DecoratorRegistered(Document):
        pass

    assert len(self.db.registered_documents) > 0
    assert self.db.registered_documents[0] == DecoratorRegistered