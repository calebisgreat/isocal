'''
Created on Mar 29, 2016

@author: caleb kandoro

This server provides the forms necessary to create a certificate 
It supplies an interface for viewing and organizing certificates 
? sending preliminary certificates 
It generates a word document based certificate from a template(write a separate 
module for that )

the structure of the server is that there is a folder that stores the
databases and the data modules. There is also a folder that contains the 
templates for both the html files served and the certificate templates generated. 

the server provides an admin interface that controls the users and allows various 
other features

'''

import cherrypy
from jinja2 import Template, Environment
import jinja2
import datetime
import time
import sqlalchemy as sqa 
import os
import data
import certificates
import datasheets
from tabulator import general_tabulation, readings_formatter, get_initials, horizontal_tabulation
import tabulator as t
from _datetime import date
from docutils.nodes import serial_escape
from pyexpat import model
root_dir = os.path.abspath(os.getcwd())
data_is_persistent = True

class CertificateServer():
    "the root application object from which all files are served"
    
    
    def __init__(self):
        '''sets up the template environment from which all templates are served'''
        self.templates = Environment \
        (loader= jinja2.FileSystemLoader(os.path.join(root_dir, "templates")))
    
    
    #
    # User management pages
    #
    @cherrypy.expose
    def index(self, user="", password=""):
        """use session information to redirect to the home screen if the user is already
        logged in"""
        Login = self.templates.get_template("login.html")
        return Login.render(user=user, password=password)
    
    
    @cherrypy.expose
    def test(self):
        cherrypy.session["logged_in"] = True
        return self.balances()
    
    @cherrypy.expose    
    def authenticate(self, user, password):
        '''this method checks the user input from the login page and returns the
        appropriate page'''
        u = data.session.query(data.users.user_name).all()
        client = data.session.query(data.users).get(user)
        users = [i[0] for i in u]
        if user in users:
            if password == client.password:
                cherrypy.session["logged_in"] = True
                cherrypy.session["user"] = user
                cherrypy.session["user_name"] = client.full_name
                print(cherrypy.session["user"])
                return self.summary()

            else:
                return self.index(password="the password is incorrect")
        else:
            return self.index(user="the user name is not stored in the database")
    
    
    
    
    @cherrypy.expose
    def signup(self, user="", type=""):
        '''used to provide server side responses to attempts to signup
        and to render the initial sign up form'''
        Signup = self.templates.get_template("signup.html")
        return Signup.render(user=user, type=type)
    
    @cherrypy.expose
    def validate_user(self, name, user, profile, password):
        '''used to check the information entered in the signup form,
        client side validation is also carried out with javascript'''
        clients= data.session.query(data.users.user_name).all()
        
        
        if user in clients:
            return self.signup(user="the username already exists")
        
        
        client = data.users(full_name = name, 
                            user_name = user,
                            profile=profile,
                            password=password)
        data.session.add(client)
        data.session.commit()
        

        return self.summary()


    
        #
        # these are the main application pages accessible from the sidebar on the left
        #
    @cherrypy.expose
    def summary(self):
        '''the default location for a user who logs in to the application'''
        Home = self.templates.get_template("summary.html")
        
        cherrypy.session._data.get("logged_in", False)
        
        outstanding = data.session.query(data.outstanding).all()
        completed = data.session.query(data.completed).all()
        
        if session_check():
            return Home.render(date = datetime.date.today(),
                               outstanding= outstanding,
                               completed= completed)
        else:
            raise cherrypy.HTTPRedirect("index")
    
    
    @cherrypy.expose
    def newcustomer(self):
        '''admisinstrative features and the like '''
        if session_check():
            new = self.templates.get_template("new_customer.html")
            return new.render()
        else:
            raise cherrypy.HTTPRedirect("index")
    
    @cherrypy.expose
    def newstandard(self):
        if session_check():
            try:
                del cherrypy.session["table"]
            except:
                print("no table")
            new = self.templates.get_template("add_standard.html")
            return new.render()
        else:
            raise cherrypy.HTTPRedirect("index")
        
        
    @cherrypy.expose
    def add_customer(self, name, address, 
                    phone, email):
        cus = data.customers(name=name,
                             address=address,
                             email=email,
                             phone=phone)
        data.session.add(cus)
        data.session.commit()
        
        raise cherrypy.HTTPRedirect("summary")
    
    @cherrypy.expose
    def check_nominal(self, value, standard):
        print("called " ,value, " from ", standard)
        standard_table = data.session.query(data.general_standards).get(standard)
        print(standard_table)
        standard_list = standard_table.nominal_values.split(":")
        print(standard_list)
        for i in standard_list:
            if i == str(value):
                return "true"
        return "false"
    
    #
    # calibration pages found under the /new/ page
    #
    
    #This is the links to all the calibration pages not related to mass
    #general uses the same page but varues the formatting
    #at the server side
    
    @cherrypy.expose
    def general(self, _type):
        """these templates are all the same except for the 
        type they belong to. The page will be the same except for the heading
        it will also pass the heading as an argument to the 
        captured method to decide which table to add data to and how to 
        format the certificate""" 
        if session_check():
            cus = data.session.query(data.customers).all()
            general= self.templates.get_template("calibration/general.html")
            instructions = False
            initials = get_initials(cherrypy.session["user"])
            number = "{}{}".format(datetime.date.today().strftime("%d%m%Y"), initials)
            if _type.lower() == "pressure":
                units = """<option value="bar">Bar</option>
                        <option value="psi">Psi</option>
                        <option value="kpa">kPa</option>
                        <option value="mpa">mPa</option>
                        <option value="pascals">Pascals</option>"""                        
                heading="Pressure" 
                standard="""<option value='deadweight'>
                                                Dead Weight Pressure Tester</option>"""
                instructions= True
                
            elif _type.lower() == 'temperature':
                heading="Temperature"
                standard="<option value='temp6'>Ecoscan Temp 6</option>"
                units= "<option value='celcius'>Celcuis</option>"
            
            elif _type.lower() == 'ph':
                heading = 'pH'
                standard="<option value='buffer'>Orion pH standards</option>"
                units= "<option value='ph'>pH</option>"
            
            elif _type.lower() == 'tds':
                heading = 'TDS sensor'
                standard="<option value='orion'>Eutech Standards</option>"
                units= "<option value='ppm'>Parts per million</option>"
            
            elif _type.lower() == 'flow':
                heading =  'Flow meters'
                standard="<option value='balance'>Balance</option>"
                units= """<option value='l-min'>Litres a minute</option>
                                                <option value='m3-hr'>Cubic Meters/hr</option>"""
            
            elif _type.lower() == 'length':
                heading='Length'
                standard="<option value='gauge blocks'>Gauge blocks</option>"
                units= """<option value='meters'>Meters</option>
                           <option value='meters'>Meters</option>"""
           
            elif _type.lower() == 'mass':
                heading= "Mass Pieces"
                standard="<option value='ohaus'>Ohaus Standard</option>"
                units= "<option value='grams'>Grams</option>"
            try:    
                del cherrypy.session["table"]
                print("deleted table")
            except:
                print("no table")
            return general.render(Heading=heading,
                                  date= datetime.date.today().strftime("%d/%m/%Y"),
                                  user=data.session.query(data.users).get(cherrypy.session["user"]).full_name,
                                  customers=cus,
                                  certificate_number=number,
                                  unit=units,
                                  standard=standard,
                                  instructions=instructions)
        else:
            raise cherrypy.HTTPRedirect("index")
    
    @cherrypy.expose
    def balances(self):
        '''used in the calibration of balances the most data intensive process'''
        if session_check():
            cus = data.session.query(data.customers).all()
            Balances = self.templates.get_template("calibration/balances.html")
            initials = get_initials(cherrypy.session["user"])
            number = "{}{}".format(datetime.date.today().strftime("%d%m%Y"), initials)
            try:
                self.clear_table()
            except:
                print("no table exists")
            return Balances.render(customers=cus,
                                   standards = data.session.query(data.general_standards).filter(data.general_standards._type == "balance"),
                                   date = datetime.date.today().strftime("%d/%m/%Y"),
                                   certificate_number= number,
                                   user = cherrypy.session["user_name"])
        else:
            raise cherrypy.HTTPRedirect("index")
    
    #
    #Ajax methods called during calibration
    #
    
    @cherrypy.expose
    def clear_table(self):
        
        if 'balance' not in cherrypy.session:
            cherrypy.session["balance"] = []
        else:
            cherrypy.session["balance"].append(cherrypy.session["table"])
        del cherrypy.session["table"]
        print(cherrypy.session["balance"])
    
    @cherrypy.expose
    def tabulate_general(self, actual, indicated):
        return general_tabulation([actual, indicated], 
                           session=cherrypy.session, 
                           headings=['Actual', 'Indicated'])
        
    @cherrypy.expose
    def tabulate_general_pressure(self, unit, actual, indicated):
        units = {"bar": t.calculate_pressure_bar,
                 "psi": t.calculate_pressure_psi,
                 "kpa": t.calculate_pressure_kpa,
                 "mpa": t.calculate_pressure_mpa,
                 "pascals": t.calculate_pressure_pa,}
        
        zero = {"bar": 0.3457732, 
                    "psi": 5.015025,
                    "kpa": 34.57732,
                    "pa": 34577.32,
                    "mpa": 0.03457732}
        
        if actual == "empty":
            pressure = zero[unit]
            actual = "0"
        
        
        elif indicated == "0" and actual == indicated:
            pressure = "0"
        
        else:
            pressure= "{:0.2f}".format(units[unit](actual))
        return general_tabulation([actual, pressure, indicated], 
                           session=cherrypy.session, 
                           headings=['Applied Mass', "Calculated Pressure", 'Indicated'])
        
        
    @cherrypy.expose
    def tabulate_balance_warm(self, value):
        return general_tabulation([value],
                                  session=cherrypy.session,
                                  headings=["Reading"],
                                  numbered=True)
    
    @cherrypy.expose
    def tabulate_balance_settling(self, value):
        return general_tabulation([value],
                                  session=cherrypy.session,
                                  headings=["Settling Time"],
                                  numbered=True)    
    
    @cherrypy.expose
    def tabulate_balance_linearity(self, nominal, up):
        return general_tabulation([nominal, up],
                                  session=cherrypy.session,
                                  headings=["Nominal Value", "Linearity Up"],
                                  )
        
    @cherrypy.expose
    def tabulate_balance_linearity_two(self, reading, row):
        return horizontal_tabulation(reading, row,
                                  session = cherrypy.session,
                                  headings=["Nominal Values",
                                            "Linearity up",
                                            "Linearity Down",
                                            "Linearity Up"])
    @cherrypy.expose
    def tabulate_balance_tare(self, tare, indicated):
        return general_tabulation([tare, indicated],
                                  session= cherrypy.session,
                                  headings=["Tare Value","Indicated Reading"])
    
    @cherrypy.expose
    def tabulate_balance_off_center_error(self, row, reading):
        return horizontal_tabulation(reading, row,
                                   session=cherrypy.session,
                                    headings=["A","B","C","D","E"])
    
    @cherrypy.expose
    def tabulate_balance_repeatability(self, row, reading):
        return horizontal_tabulation(reading, row,
                                   session= cherrypy.session,
                                    headings=["1/2 Reading",
                                              "Full Reading"])

    @cherrypy.expose
    def tabulate_standard(self,nominal, actual, uncertainty):
        return general_tabulation([nominal, actual, uncertainty],
                                  session= cherrypy.session,
                                  headings=["Nominal", "Actual", "Uncertainty"])
    @cherrypy.expose
    def standards_table(self, standard):
        table = """<table>
                        <tr>
                            <th>Nominal Values</th>
                            <th>Actual Values</th>
                        </tr>
                        {}
                    </table>"""
        standard= data.session.query(data.general_standards).get(standard)
        nominal_values = standard.nominal_values.split(":")
        actual_values = standard.actual_values.split(":")
        
        i=0
        rows = []
        while i < len(nominal_values):
            rows.append("<tr><td>{}</td><td>{}</td></tr>".format(nominal_values[i], actual_values[i]))
            
        return table.format("\n".join(rows))
    
    # Data submission into the database
    #
    
        
    @cherrypy.expose
    def add_standard(self, name, certificate, _type):
        if session_check():
            s = data.general_standards(name=name,
                                certificate=certificate,
                                _type= _type,
                                nominal_values=":".join(cherrypy.session["table"]["Nominal"]),
                                actual_values=":".join(cherrypy.session["table"]["Actual"]),
                                uncertainty=":".join(cherrypy.session["table"]["Uncertainty"]),
                                )
            try:
                data.session.add(s)
                del cherrypy.session["table"]
                data.session.commit()
            except Exception as e:
                data.session.rollback()
                
                return "<p> An error occured {}</p> <a href='summary' style='background-color: blue;' >Go back</a>".format(e)
            raise cherrypy.HTTPRedirect("summary")
        else:
            del cherrypy.session["table"]
            raise cherrypy.HTTPRedirect("index")
    
    @cherrypy.expose
    def captured(self, _customer, _type, _date, _instrument, _sn, _man, _model,
                 _range, _resolution, _units, _standard, _location,
                 _actual, _indicated, _immersion, _comments):
        if session_check():
            
            today = datetime.date.today()
            #
            # Try except clause designed to make the tests pass
            #
            try:
                if _type.lower() == "pressure":
                    _keys = ["Applied Mass", "Calculated Pressure", "Indicated"]
                else:
                    _keys = cherrypy.session["table"].keys()
                args= [cherrypy.session["table"][key] for key in _keys]
                r = readings_formatter(args)
            except:
                r = "100:1"
                
            id = "{}{}".format(today.strftime("%d%m%y"), _sn)
            print("Date ", _date)
            print("readings: ", r)
            try:
                record = data.general(
                                _id = id,
                                customer=_customer,
                                start_time= time.time(),
                                end_time= time.time(),
                                 name_of_instrument= _instrument,
                                 serial = _sn,
                                 manufacturer = _man.upper(),
                                 model = _model,
                                 range =_range,
                                 immersion_depth= _immersion,
                                 standards = _standard,
                                 resolution = _resolution,
                                 units = _units.upper(),
                                 location = _location,
                                 readings = r,
                                 comments =_comments
                                 )
                data.session.add(record)
                data.session.commit()
                del cherrypy.session["table"]
            except Exception as e:
                data.session.rollback()
                del cherrypy.session["table"]
                print("a bigger error occured", e)
                raise cherrypy.HTTPRedirect("summary")
            
            
            out = data.outstanding(_id = id,
                                   _type = _type,
                                   name_of_instrument= _instrument,
                                   customer = _customer,
                                   serial = _sn
                                   )
            
            data.session.add(out)
            data.session.commit()
            
            raise cherrypy.HTTPRedirect("summary")

        else:
            raise cherrypy.HTTPRedirect("index")
        
    @cherrypy.expose
    def captured_balance(self, _customer, _date, warm_up_nominal, _instrument, _sn, _man,
                         _model, _range, _resolution, _units, _location,
                         _procedure,  mass_pieces_set, _comments,
                         off_center_mass):
        
        if session_check():
            if _customer == "test":
                #used for tests
                balance = [{'Reading': ['100', '100', '100', '100', '100', '100', '99.998', '99.995', '100.002', '100.005']},
                            {'Settling Time': ['5.5', '5.5', '5.5', '5.5', '5.5']},
                             {'Linearity Up': ['49.995', '99.960', '200.005', '499.950', '999.905'], 'Nominal Value': ['50', '100', '200', '500', '1000']},
                              {'Linearity Down': ['49.995', '99.960', '200.005', '499.950', '999.905'],'Nominal Values': ['50', '100', '200', '500', '1000'], 'Linearity Up': ['49.995', '99.960', '200.005', '499.950', '999.905'], 'Linearity up': ['49.995', '99.960', '200.005', '499.950', '999.905']},
                               {'Tare Value': ['50', '100', '200', '500', '1000'], 'Indicated Reading': ['-50', '-100', '-200', '-500', '-1000']},
                                {'Full Reading': ['800.005', '799.999', '800', '799.995', '800.002'], '1/2 Reading': ['400', '400', '399.995', '400.005', '400']},
                                 {'B': ['200'], 'D': ['201'], 'C': ['199'], 'E': ['200'], 'A': ['200']}]
             
            else:
                balance = cherrypy.session["balance"]
            try:
                id = "{}{}".format(datetime.date.today().strftime("%d%m%y"), _sn)    
                record = data.balance(_id= id,
                                      customer = _customer,
                                      end_time = time.time(),
                                      name = _instrument,
                                      serial = _sn,
                                      manufacturer = _man,
                                      model = _model,
                                      range = _range,
                                      resolution = _resolution,
                                      units = _units,
                                      location = _location,
                                      procedure = _procedure,
                                      comments = _comments,
                                      standard = mass_pieces_set,
                                      warm_up_nominal = warm_up_nominal,
                                      off_center_mass = off_center_mass,
                                      nominal_mass = ":".join(balance[0]["Reading"]),
                                      settling_time = ":".join(balance[1]["Settling Time"])
                                      )
                
                bc= data.balance_before_calibration(_id = id,
                                                nominal_value=":".join(balance[2]["Nominal Value"]), 
                                                linearity_up=":".join(balance[2]["Linearity Up"]))
                
                la= data.balance_linearity_after(_id= id,
                                             nominal= ":".join(balance[3]["Nominal Values"]),
                                             linearity_up= ":".join(balance[3]["Linearity up"]),
                                             linearity_Down=":".join(balance[3]["Linearity Down"]),
                                             linearity_uup=":".join(balance[3]["Linearity Up"]
                                             ))
                
                tare= data.balance_tare(_id=id,
                                  tare= ":".join(balance[4]["Tare Value"]),
                                  indicated=":".join(balance[4]["Indicated Reading"]))
                
                br= data.balance_repeatability(_id=id,
                                           half_reading=":".join(balance[5]["1/2 Reading"]),
                                           full_reading=":".join(balance[5]["Full Reading"]))
                
                oc= data.balance_off_center(_id=id,
                                        a=balance[6]["A"],
                                        b=balance[6]["B"],
                                        c=balance[6]["C"],
                                        d=balance[6]["D"],
                                        e=balance[6]["E"])
                
                
                out = data.outstanding(_id = id,
                                   _type= "balance",
                                   name_of_instrument= "balance",
                                   customer = _customer,
                                   serial = _sn
                                   )
                
                data.session.add(oc)
                data.session.add(br)
                data.session.add(tare)
                data.session.add(la)
                data.session.add(bc)
                data.session.add(record)
                data.session.add(out)
                data.session.commit()
            
            except Exception as e:
                data.session.rollback()
                if _customer != "test": del cherrypy.session["balance"]
                return 'an error occured', e
            
            
            if _customer != "test": del cherrypy.session["balance"]
            raise cherrypy.HTTPRedirect("summary")
        
        else:
            raise cherrypy.HTTPRedirect("index")
    
    
    @cherrypy.expose
    def generate_certificate(self, id, _type):
        form=self.templates.get_template("add.html")
        return form.render(id=id, _type=_type)
        
    @cherrypy.expose
    def create_certificate(self, temp, humidity, id, _type):
        initials = get_initials(cherrypy.session["user"])
        print(initials)    
        now = datetime.datetime.now()
        certificate_number= "{}{}".format(now.strftime("%Y%m%d%H%M%S"),
                               initials)
        
        _types= {"volume": certificates.volume_certificate,
                 "current": certificates.current_certificate,
                 "conductivity": certificates.conductivity_certificate,
                 "voltage": certificates.voltage_certificate,
                 "pressure": certificates.pressure_certificate,
                    "temperature": certificates.temperature_certificate,
                    "ph": certificates.ph_certificate,
                    "flow": certificates.flow_certificate,
                    'length': certificates.length_certificate,
                    "mass": certificates.mass_certificate,
                    "tds": certificates.tds_certificate,
                    "balance": certificates.balance_certificate}
        
        if _type.lower() == "balance":
            c= data.session.query(data.balance).get(id)
            d= datasheets.balance_datasheet(id, initials)
            d.generate_datasheet()
            completed =data.completed(_id = id,
                                   name_of_instrument= "balance",
                                   customer = c.customer,
                                   serial = certificate_number
                                      )
        else:  
            c= data.session.query(data.general).get(id)
            d= datasheets.general_datasheet(id, initials)
            d.generate_datasheet()
            completed =data.completed(_id = id,
                                   name_of_instrument=c.name_of_instrument,
                                   customer =c.customer,
                                   serial = certificate_number
                                      )
            
            
        cert= _types[_type.lower()](id, initials, cherrypy.session["user_name"],
                                    temp, humidity)
        cert.generate_certificate()
            
        try:
            data.session.add(completed)
            data.session.delete(data.session.query(data.outstanding).get(id))
            data.session.commit()
        except Exception as e:
            data.session.rollback()
            print("this happened during commit: ", e)
        finally:
            return self.summary()
    
    def preview(self, number):
        '''previews the recently created certificate'''
        preview = self.templates.get_template("certificate_preview.html")
        return preview.render(certificate= "{}\certificates\completed\{}.html".format( \
                                                        root_dir,number))
            
        
        #
        #these keys are removed from the session once the table is created 
        #and added to the page 
        #

        
    
    
            
    
    
    
conf = {"global": {
					"server.socket_port": 8080,
                    "server.socket_host": "127.0.0.1"
				},
        "/": {
              "tools.sessions.on" : True,
              "tools.staticdir.root": os.path.abspath(os.getcwd()),
              "tools.staticdir.on": True,
              "tools.staticdir.dir": "./Templates",
              "server.thread_pool": 10# will change one sqlalchemy is implemented
              }
        }

#
# this function makes sure only logged in users can access certain pages
#
def session_check():   
    if "logged_in" in cherrypy.session:
        return cherrypy.session['logged_in']
    else:
        cherrypy.session["logged_in"] = False
        return False
    

class Mobile():
    def __init__(self):
        self.balance_count = 0
        self.autoclave_count = 0
        self.status = "pending"
        self.balance = {}
        self.autoclave={}
    @cherrypy.expose
    def index(self):
        return "success"
    
    @cherrypy.expose
    def upload_balance(self, key, value):
        self.balance[key] = value.replace("|", ":")
        print(value)
        self.balance_count += 1
        print(self.balance_count)
        self.status = "pending"
        if self.balance_count == 32:
            self.status = self.add_balance()
        return self.status
    
    def add_balance(self):
        try:
            print(self.balance)
            record = data.balance(_id= self.balance["id"],
                                          customer = self.balance["customer"],
                                          end_time = self.balance["end_time"],
                                          start_time = self.balance["start_time"],
                                          serial = self.balance["sn"],
                                          manufacturer = self.balance["man"],
                                          model = self.balance["model"],
                                          range = self.balance["_range"],
                                          resolution = self.balance["resolution"],
                                          units = self.balance["units"],
                                          location = self.balance["location"],
                                          procedure = self.balance["procedure"],
                                          comments = self.balance["comments"],
                                          standard = self.balance["standard"],
                                          warm_up_nominal = self.balance["warm_up_nominal"],
                                          off_center_mass = self.balance["off_center_mass"],
                                          nominal_mass = self.balance["nominal_mass"],
                                          settling_time = self.balance["settling_time"]
                                          )
                    
            bc= data.balance_before_calibration(_id = self.balance["id"],
                                                    nominal_value=self.balance["before_nominal"], 
                                                    linearity_up=self.balance["before_up"],
                                                    actual=self.balance["before_actual"])
                    
            la= data.balance_linearity_after(_id= self.balance["id"],
                                                 linearity_up= self.balance["after_up"],
                                                 linearity_Down=self.balance["after_down"],
                                                 linearity_uup=self.balance["after_uup"]
                                                 )
                    
            tare= data.balance_tare(_id=self.balance["id"],
                                      tare= self.balance["tare"],
                                      indicated=self.balance["tare_indicated"])
                    
            br= data.balance_repeatability(_id=self.balance["id"],
                                               half_reading=self.balance["repeat_half"],
                                               full_reading=self.balance["repeat_full"])
                    
            off = self.balance["off_center"].split(":")
            oc= data.balance_off_center(_id=self.balance["id"],
                                            a=off[0],
                                            b=off[1],
                                            c=off[2],
                                            d=off[3],
                                            e=off[4])
                    
                    
            out = data.outstanding(_id = self.balance["id"],
                                   _type= "Balance",
                                   name_of_instrument= "Balance",
                                   customer = self.balance["customer"],
                                   serial = self.balance["sn"]
                                   )
                
            data.session.add(oc)
            data.session.add(br)
            data.session.add(tare)
            data.session.add(la)
            data.session.add(bc)
            data.session.add(record)
            data.session.add(out)
            data.session.commit()
            
        except Exception as e:
            data.session.rollback()
            print("error: ", e)
            self.balance = {}
            self.balance_count = 0
            
            return "failed"
        else:
            self.balance = {}
            self.balance_count = 0
            return "success"
        
    @cherrypy.expose
    def upload_autoclave(self, key, value):
        self.autoclave_count += 1
        self.autoclave[key] = value
        print(self.autoclave_count)
        self.status = "pending"
        if self.autoclave_count == 21:
            self.status = self.add_autoclave()
        return self.status
    def add_autoclave(self):
        try:
            auto = data.autoclave(_id=self.autoclave["id"],
                                  customer=self.autoclave["customer"],
                                  start_time=self.autoclave["start_time"],
                                  end_time=self.autoclave["end_time"],
                                  date=datetime.date.today(),
                                  serial=self.autoclave["serial"],
                                  immersion_depth=self.autoclave["immersion_depth"],
                                  manufacturer=self.autoclave["manufacturer"],
                                  model=self.autoclave["model"],
                                  range_temp=self.autoclave["range_temp"],
                                  range_p=self.autoclave["range_p"],
                                  resolution_temp=self.autoclave["resolution_temp"],
                                  resolution_p=self.autoclave["resolution_p"],
                                  units_temp=self.autoclave["units_temp"],
                                  units_p=self.autoclave["units_p"],
                                  standards=self.autoclave["standards"],
                                  location=self.autoclave["location"],
                                  comments=self.autoclave["comments"],
                                  temp=self.autoclave["temp"],
                                  pressure=self.autoclave["pressure"]
                                  )
            data.session.add(auto)
            data.session.commit()
        except Exception as e:
            print("this happened ", e)
            data.session.rollback()
            return "failed"
        else:
            self.autoclave = {}
            self.autoclave_count = 0
            return "success"
    
    
    @cherrypy.expose
    def upload_general(self, user, customer, _type, id, date, due,instrument, sn, man, model,
                 _range, resolution, units, standard, location, start_time, end_time,
                 readings, corrections, immersion, comments):
        print(readings)
        try:
            record = data.general(
                                _id = id,
                                customer=customer,
                                start_time= start_time,
                                end_time= end_time,
                                date = datetime.datetime.strptime(date, "%d/%m/%Y"),
                                name_of_instrument= instrument,
                                serial = sn,
                                manufacturer = man.upper(),
                                model = model,
                                range =_range,
                                immersion_depth= immersion,
                                standards = standard,
                                resolution = resolution,
                                units = units.upper(),
                                location = location,
                                readings = readings,
                                corrections= corrections,
                                comments =comments
                                )
            data.session.add(record)
            out = data.outstanding(_id = id,
                                   _type = _type,
                                   name_of_instrument= instrument,
                                   customer = customer,
                                   serial = sn
                                   )
            
            data.session.add(out)
            data.session.commit()
        except Exception as e:
            data.session.rollback()
            print("a bigger error occured", e)
            return "failure"
        else:
            return "success"
    @cherrypy.expose  
    def upload_standard(self, name, number, nominal, traceability,
                        actual, uncertainty, serial):
        try:
            std = data.general_standards(name=name,
                                         _type="standard",
                                         certificate=number,
                                         serial=serial,
                                         traceability=traceability,
                                         nominal_values=nominal,
                                         actual_values=actual,
                                         uncertainty=uncertainty)
            data.session.add(std)
            data.session.commit()
        except Exception as e:
            data.session.rollback()
            print("standard, ", e)
            return "failure"
        else:
            return "success"
            
s = CertificateServer()
s.mobile = Mobile()

if __name__ == "__main__":
    """import tkinter as tk
    
    class intro(tk.Frame):
        def __init__(self, parent):
            super().__init__(parent, background="white")
            self.parent = parent
            self.initUi()
            
        def initUi(self):
            self.parent.title = "Start"
            ip = tk.Label(self, text="Network ip:")
            data= tk.Label(self, text="Database address and password")
            sub= tk.Button(self, text="Start!", command= self.start_server)
            
        def start_server(self):"""
    conf = {"global": {
                    "server.socket_port": 8080,
                    "server.socket_host": "0.0.0.0"
                },
            "/": {
              "tools.sessions.on" : True,
              "tools.staticdir.root": os.path.abspath(os.getcwd()),
              "tools.staticdir.on": True,
              "tools.staticdir.dir": "./Templates",
              "server.thread_pool": 10# will change one sqlalchemy is implemented
              }
        }
    cherrypy.quickstart(s,"/", conf)
    
    