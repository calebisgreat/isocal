'''
Created on Mar 29, 2016
yes
@author: caleb kandoro


'''
import sqlalchemy as sqa
from sqlalchemy.ext.declarative import declarative_base
import sqlite3
import datetime
import time
from sqlalchemy import Date, Time, DateTime
import random
from sqlalchemy.pool import NullPool
from sqlalchemy.orm.scoping import scoped_session


BASE= declarative_base()

class users(BASE):
    __tablename__ = "users"
    inx = sqa.Column(sqa.Integer())
    full_name = sqa.Column(sqa.String(128))# handle length wxceptions
    user_name = sqa.Column(sqa.String(64), primary_key=True)#implement a foreign key here
    profile= sqa.Column(sqa.String(32))
    password = sqa.Column(sqa.String(64))#encrypt one day
          

class customers(BASE):
    __tablename__="customers"
    name= sqa.Column(sqa.String(128), primary_key=True)
    address= sqa.Column(sqa.String(128))
    email = sqa.Column(sqa.String(128))
    phone=sqa.Column(sqa.Integer())

#
#The list of calibrations 
#	
class autoclave(BASE):
    __tablename__ = "autoclave"
    _id = sqa.Column(sqa.String(32),  primary_key = True)
    customer = sqa.Column(sqa.String(32))
    start_time = sqa.Column(sqa.String(32))
    end_time = sqa.Column(sqa.String(32))
    date = sqa.Column(Date(), default = datetime.date.today)
    serial = sqa.Column(sqa.String(24))
    immersion_depth = sqa.Column(sqa.String(24))
    manufacturer = sqa.Column(sqa.String(64))
    model = sqa.Column(sqa.String(64))
    range_temp = sqa.Column(sqa.String(12))
    range_p = sqa.Column(sqa.String(12))
    resolution_temp =sqa.Column(sqa.String(12))
    resolution_p = sqa.Column(sqa.String(12))
    units_temp = sqa.Column(sqa.String(12))
    units_p = sqa.Column(sqa.String(12))
    standards= sqa.Column(sqa.String(64))
    location = sqa.Column(sqa.String(32))
    comments = sqa.Column(sqa.String(256))
    temp = sqa.Column(sqa.String(256))
    pressure= sqa.Column(sqa.String(256))
 
class general(BASE):
    __tablename__ = "general"
    
    _id = sqa.Column(sqa.String(32),  primary_key = True)
    customer = sqa.Column(sqa.String(32))
    _type = sqa.Column(sqa.String(32))
    start_time = sqa.Column(sqa.String(32))
    end_time = sqa.Column(sqa.String(32))
    date = sqa.Column(Date(), default = datetime.date.today)
    name_of_instrument = sqa.Column(sqa.String(32))
    serial = sqa.Column(sqa.String(24))
    immersion_depth = sqa.Column(sqa.String(24))
    manufacturer = sqa.Column(sqa.String(64))
    model = sqa.Column(sqa.String(64))
    range = sqa.Column(sqa.String(12))
    resolution = sqa.Column(sqa.String(12))
    units = sqa.Column(sqa.String(12))
    standards= sqa.Column(sqa.String(64))
    location = sqa.Column(sqa.String(32))
    comments = sqa.Column(sqa.String(256))
    readings = sqa.Column(sqa.String(256))
    corrections= sqa.Column(sqa.String(256))
    

class balance(BASE):
    __tablename__= "balance"
    _id = sqa.Column(sqa.String(32),  primary_key = True)
    customer = sqa.Column(sqa.String(128))
    start_time = sqa.Column(sqa.String(32))
    end_time = sqa.Column(sqa.String(32))
    date = sqa.Column(Date(), default = datetime.date.today)
    serial = sqa.Column(sqa.String(64))
    manufacturer = sqa.Column(sqa.String(64))
    model = sqa.Column(sqa.String(64))
    range = sqa.Column(sqa.String(64))
    resolution = sqa.Column(sqa.String(64))
    units = sqa.Column(sqa.String(64))
    location = sqa.Column(sqa.String(64))
    procedure = sqa.Column(sqa.String(32))
    standard = sqa.Column(sqa.String(32))
    comments = sqa.Column(sqa.String(256))
    warm_up_nominal= sqa.Column(sqa.String(64)) # single value
    nominal_mass = sqa.Column(sqa.String(172)) # list
    settling_time = sqa.Column(sqa.String(128)) #list
    off_center_mass = sqa.Column(sqa.String(64)) # single value

class balance_before_calibration(BASE):
    __tablename__="before_calibration"
    _id = sqa.Column(sqa.String(32),primary_key = True )
    nominal_value = sqa.Column(sqa.String(128))
    linearity_up = sqa.Column(sqa.String(128))
    actual = sqa.Column(sqa.String(128))
    
class balance_linearity_after(BASE):
    __tablename__="linearity_after"
    _id = sqa.Column(sqa.String(32),  primary_key = True)
    linearity_up = sqa.Column(sqa.String(128))
    linearity_Down= sqa.Column(sqa.String(128))
    linearity_uup= sqa.Column(sqa.String(128))
    
    
class balance_tare(BASE):
    __tablename__="tare"
    _id = sqa.Column(sqa.String(32), primary_key = True)
    tare= sqa.Column(sqa.String(128))
    indicated= sqa.Column(sqa.String(128))
    
    
class balance_repeatability(BASE):
    __tablename__="repeatability"
    _id = sqa.Column(sqa.String(32),  primary_key = True)
    half_reading= sqa.Column(sqa.String(128))
    full_reading= sqa.Column(sqa.String(128))
    
class balance_off_center(BASE):
    __tablename__="off_center"
    _id = sqa.Column(sqa.String(32), primary_key = True)
    a= sqa.Column(sqa.String(18))
    b= sqa.Column(sqa.String(18))
    c= sqa.Column(sqa.String(18))
    d= sqa.Column(sqa.String(18))
    e= sqa.Column(sqa.String(18))
    
    
class completed(BASE):
    __tablename__ ="completed"
    _id = sqa.Column(sqa.String(32),  primary_key = True)
    name_of_instrument = sqa.Column(sqa.String(32))
    customer = sqa.Column(sqa.String(128))
    serial = sqa.Column(sqa.String(64))
    date = sqa.Column(Date(), default = datetime.date.today())
    
    
class outstanding(BASE):
    __tablename__ = "outstanding"
    _type= sqa.Column(sqa.String(24))
    _id = sqa.Column(sqa.String(32),  primary_key = True)
    name_of_instrument = sqa.Column(sqa.String(32))
    customer = sqa.Column(sqa.String(128))
    serial = sqa.Column(sqa.String(64))
    date = sqa.Column(Date(), default = datetime.date.today())


class general_standards(BASE):
    __tablename__ ="general_standards"
    name = sqa.Column(sqa.String(32), primary_key=True)
    _type = sqa.Column(sqa.String(32))
    certificate = sqa.Column(sqa.String(256))
    serial=sqa.Column(sqa.String(32))
    traceability = sqa.Column(sqa.String(256))
    nominal_values = sqa.Column(sqa.String(256))
    actual_values = sqa.Column(sqa.String(256))
    uncertainty = sqa.Column(sqa.String(256))


#    
#the tables that provide the list of measured data
#


engine = sqa.create_engine("sqlite:///isocal.db", poolclass = NullPool)#dont forget to change!    
BASE.metadata.create_all(engine)
SESSION = sqa.orm.sessionmaker(bind=engine)
session = scoped_session(SESSION)

if __name__ == "__main__":
    base = {"_id": "1",
            "customer": 'Delta',
            "start_time":"20:30",
            "end_time":"20:35",
            "date": datetime.date.today(),
            "serial": "0123",
            "immersion_depth": "-",
            "manufacturer": "man",
            "model": "mod",
            "range": "0-100",
            "resolution": "0.01",
            "standards": "standard",
            "location": "delta",
            "comments": "none"}
    
    pressure= {"name_of_instrument": "pressure gauge",
               "readings": "0:0:0;2398:4.03:4",
               "corrections": "0:0:0;2398:4.03:4",
               "units": "bar",
               "_type": "pressure"}
    
    mass={"name_of_instrument": "ohaus",
               "readings": "100.0001:100.0001;99.9999:99.9999",
               "units": "grams",
               "_type": "mass"}
    
    temperature={"name_of_instrument": "water bath",
               "readings": "25:25;50:52",
               "corrections": "25:25;50:52",
               "units": "celcius",
               "_type": "temperature"}
    
    flow={"name_of_instrument": "flow meter",
               "readings": "0.2:0.2;0.45:0.5",
               "corrections": "0.2:0.2;0.45:0.5",
               "units": "l/min",
               "_type": "flow"}
    
    volume={"name_of_instrument": "micropippette",
               "readings": "10:10;50:50",
               "corrections": "10:10;50:50",
               "units": "ul",
               "_type": "volume"}
    
    current={"name_of_instrument": "ammeter",
               "readings": "2:2;5:5",
               "corrections": "2:2;5:5",
               "units": "ampere",
               "_type": "current"}
    
    voltage= {"name_of_instrument": "voltmeter",
               "corrections": "55:50;205:200",
               "readings": "55:50;205:200",
               "units": "volt",
               "_type": "voltage"}
    
    ph= {"name_of_instrument": "PH meter",
                
               "corrections": "3.01:3.5;10.4:10",
               "readings": "3.01:3.5;10.4:10",
               "units": "ph",
               "_type": "ph"}
    
    tds={"name_of_instrument": "TDS Meter",
               "readings": "205:200;800:807",
               "corrections": "205:200;800:807",
               "units": "ppt",
               "_type": "tds"}
    
    length={"name_of_instrument": "Micrometer",
               "readings": "205:200;800:807",
               "corrections": "205:200;800:807",
               "units": "m",
               "_type": "length"}
    
    conductivity={"name_of_instrument": "conductivity meter",
               "readings": "0:0;23:25",
               "corrections": "0:0;23:25",
               "units": "siemens",
               "_type": "conductivity"}
    
    
    auto = {"_id": "123456",
            "customer": "delta",
            "start_time": "20:05",
            "end_time": "20:10",
            "date": datetime.date.today(),
            "serial":"789",
            "immersion_depth": "-",
            "manufacturer": "man",
            "model": "mod",
            "range_temp": "0-100",
            "range_p": "0-10",
            "resolution_temp": "0.1",
            "resolution_p": "0.5",
            "units_temp": "C",
            "units_p": "bar",
            "standards": "dead weight",
            "location": "delta",
            "comments": "ok",
            "temp": "10:10;50:52",
            "pressure": "1250:2.5:2;4600:7:7"}

    gen = [mass, pressure, voltage, current, ph, tds, length, volume, conductivity, flow, temperature]

    """for i in gen:
        base.update(i)
        base["_id"] = str(random.randint(0, 100000))
        session.add(general(**base))
        session.commit()
        print("created")"""
        
    
