from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, scoped_session

from geoalchemy import GeometryColumn, Geometry

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

GPS_SCHEMA = 'gps'


class Individual(Base):
    __tablename__ = 'uva_individual'
    __table_args__ = {'schema': GPS_SCHEMA}
    ring_number = Column(String, primary_key=True)
    color_ring = Column(String)
    species = Column(String)
    sex = Column(String)


class Device(Base):
    __tablename__ = 'uva_device'
    __table_args__ = {'schema': GPS_SCHEMA}

    device_info_serial = Column(Integer, primary_key=True)
    #project_key_name = Column(String, ForeignKey(Project.key_name))


class TrackSession(Base):
    __tablename__ = 'uva_track_session'
    __table_args__ = {'schema': GPS_SCHEMA}

    device_info_serial = Column(Integer,
                                ForeignKey(Device.device_info_serial),
                                primary_key=True,
                                )
    ring_number = Column(String,
                         ForeignKey(Individual.ring_number),
                         primary_key=True,
                         )


class Track(Base):
    __tablename__ = 'uva_tracking_speed'
    __table_args__ = {'schema': GPS_SCHEMA}
    device_info_serial = Column(Integer, ForeignKey(Device.device_info_serial), primary_key=True)
    date_time = Column(DateTime, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    location = GeometryColumn(Geometry(3))
    pressure = Column(Float)
    temperature = Column(Float)
    speed = Column(Float)
    speed3d = Column(Float)
    direction = Column(Float)

