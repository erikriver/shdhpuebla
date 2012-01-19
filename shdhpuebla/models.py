from sqlalchemy import Column, Integer, Text, DateTime, Boolean, String, ForeignKey, UnicodeText, Unicode

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import relationship, backref

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Event(Base):
    __tablename__ = 'event'
    id      = Column(Integer, primary_key=True)
    name    = Column(Unicode(255))
    city    = Column(Unicode(255))
    start   = Column(DateTime)
    end     = Column(DateTime)
    lat     = Column(String(255))
    lon     = Column(String(255))
    active  = Column(Boolean)
    attendees = relationship("Attendance", order_by="Attendance.id", backref="event")

class Attendance(Base):
    __tablename__ = 'attendance'
    id          = Column(Integer, primary_key=True)
    event_id    = Column(Integer, ForeignKey('event.id'))
    network     = Column(String(255))
    token       = Column(String(255))
    token_secret = Column(String(255))
    user_id     = Column(Unicode(255))
    user_name   = Column(Unicode(255))
    url         = Column(Unicode(255))
    email       = Column(Unicode(255))
    image_url   = Column(Text)
    tasks       = Column(UnicodeText)
