import unittest
import transaction

from pyramid import testing

from .models import DBSession

class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import Base, Event, Attendance
        
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            event = Event(name=u'Primera Edici&oacute;n', city=u'Puebla, Pue.',start=datetime(2012,02,11,9,0), end=datetime(2012,02,11,21,0), active=True)
            DBSession.add(event)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from .views import index
        request = testing.DummyRequest()
        index = index(request)
        self.assertEqual(index['one'].name, u'Primera Edici&oacute;n')
        self.assertTrue(index['project'].active)
