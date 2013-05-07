from sqlalchemy import (
    Column,
    Integer,
    Text,
    )
from sqlalchemy import Float
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Track(Base):
    __tablename__ = 'track'
    id = Column(Text, primary_key=True)
    tid = Column(Integer)
    name = Column(Text)
    utm_time = Column(Text)
    classifier = Column(Text)
    lat = Column(Float)
    long = Column(Float)
    alt = Column(Float)
    temp = Column(Float)
    speed = Column(Float)
    speed3d = Column(Float)
