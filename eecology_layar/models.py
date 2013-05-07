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
from geoalchemy import GeometryColumn, Point

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Track(Base):
    __tablename__ = 'gps.uva_tracking_speed'
    device_info_serial = Column(Integer, primary_key=True)
    date_time = Column(Text, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    # TODO enable when using PostGIS
    # location = GeometryColumn(Point(3))
    temperature = Column(Float)
    speed = Column(Float)
    speed3d = Column(Float)
    direction = Column(Float)
    # columns need to be moved to other tables
    classifier = Column(Text)
    name = Column(Text)


class Individual(Base):
    __tablename__ = 'gps.uva_individual'
    ring_number = Column(Text, primary_key=True)
    color_ring = Column(Text)
    species = Column(Text)
    sex = Column(Text)
