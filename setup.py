"""
Flask-MongoKit
--------------

Flask-MongoKit make it simpler to integrate the MongoDB ODM into Flask.

"""
from setuptools import setup


setup(
    name='Flask-MongoKit',
    version='0.2',
    url='http://bitbucket.org/Jarus/flask-mongokit',
    license='BSD',
    author='Christoph Heer',
    author_email='Christoph.Heer@googlemail.com',
    description='Flask extension to better integrate MongoKit into Flask',
    long_description=__doc__,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'MongoKit'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)