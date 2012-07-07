import sys
import unittest
from flask import Flask

from test_base import *

if sys.version_info > (2, 6):
    from test_decorator_registration import decorator_registration
    setattr(TestCaseContextIndependent, 'test_decorator_registration', 
            decorator_registration)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCaseContextIndependent))
    suite.addTest(unittest.makeSuite(TestCaseInitAppWithRequestContext))
    suite.addTest(unittest.makeSuite(TestCaseWithRequestContext))
    suite.addTest(unittest.makeSuite(TestCaseWithRequestContextAuth))
    suite.addTest(unittest.makeSuite(TestCaseMultipleAppsWithRequestContext))
    if hasattr(Flask, "app_context"):
        suite.addTest(unittest.makeSuite(TestCaseInitAppWithAppContext))
        suite.addTest(unittest.makeSuite(TestCaseWithAppContext))
        suite.addTest(unittest.makeSuite(TestCaseWithAppContextAuth))
        suite.addTest(unittest.makeSuite(TestCaseMultipleAppsWithAppContext))
    return suite

