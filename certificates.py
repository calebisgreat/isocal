'''
Created on Apr 1, 2016

@author: caleb kandoro
'''

import data
from tabulator import general_tabulation, horizontal_tabulation
import datetime 
import time
import jinja2
import os
import math
from statistics import stdev, mean
from builtins import round

DIR = os.path.abspath(os.getcwd())

templates = jinja2.Environment(loader= jinja2.FileSystemLoader \
                               (os.path.join(DIR, "certificates\\templates")))


"""this module contains the base class for all certificates modelled around the template
design pattern. It also includes the classes for the  """
    
class certificate():
    
    def __init__(self, _id, initials, by, temp, humidity):
        
        
        '''THE BASE object from which common certificate features are abstracted
        the __init__ function obtains the row from the table where the data is 
        recorded
        the class refers to the table from which all database queries will be 
        made. NB the databases use the serial number as a primary key'''

        self.id = _id
        self.today = datetime.date.today()
        self.initials = initials
        self.certificate_number(self.initials)
        self.calculator_input = []
        self.calculator_output = []
        self.template = None
        self.calibrator = by
        self.temp = temp
        self.humidity =humidity
        
        
    def certificate_number(self, initials):
        now = datetime.datetime.now()
        self.certificate_number= "{}{}".format(now.strftime("%Y%m%d%H%M%S"),
                               self.initials)
        
    def get_data(self, table, key):
        self.data = data.session.query(table).get(key)
        print("readings: ", self.data.readings)
        print(self.data.location)
        try:
            #get standards data
            d = data.session.query(data.general_standards).get(self.data.standards)
            self.standard = """"<tr>
                        <td class='no_b'>{}</td>
                        <td class='no_b'>{}</td>
                        <td class='no_b'>{}</td>
                </tr>""".format(d.name, 
                                d.serial,
                                d.certificate)
            self.traceability = d.traceability
        except:
            self.standard = "<tr><td class='no_b'>" + self.data.standards + "</td><td class='no_b'></td><td class='no_b'></td></tr>"
            self.traceability= ""
            
    def extract_readings(self):
        '''each table has a readings string may be able to generalize 
        it with time, but for now stick with individual implementations
        each implementation interface must take a set of input readings 
        extracted and place them in the self.calculator_input list whether 
        or not the input is going to be modified'''
        table = self.data.readings
        rows = table.split(";")
        print("rows: ", rows)
        self.indicated = []
        self.calculator_input = []
        for row in rows:
            print("row: ", row)
            cells = row.split(":")
            self.indicated.append(float(cells[1]))
            try:
                self.calculator_input.append(float(cells[0]))
            except:
                self.calculator_input.append(0.0)
                
        print("indicated: ", self.indicated)
        
    def calculate(self):
        '''all the calculations are performed in this method
        if they are many they can be implemented in their own methods 
        and called from here
        the calculations use self.calculator_input list based on readings
        and iterate calculations on that list, placing the results in 
        self.calculator_output'''
        self.calculator_output = self.calculator_input

    def uncertainty(self):
        '''all uncertainty calculations are performed in this method'''
        '''will calculate the uncertainty based on the recorded data'''
        
        length = len(self.indicated)
        largest_difference = 0
        self.corrections = []
        i = 0
        while i < length:
            difference = abs(self.calculator_output[i] - self.indicated[i])
            
            if difference > largest_difference:
                largest_difference = difference
                
            self.corrections.append(difference)
            i += 1
        squared = [math.pow(i, 2) for i in self.corrections]
        squared.append(float(self.data.resolution))
        self._uncertainty = "{:0.4f}".format(math.sqrt(sum(squared)))
                                    
            
    def generate_table(self):
        table = "<tr>{}</tr>"
        rows = []
        i= 0 
        while i < len(self.calculator_input):
            row = "<td>{:0.1f}</td><td>{:0.1f}</td><td>{:0.4f}</td>".format(self.calculator_input[i], 
                                                            self.indicated[i],
                                                            float(self.corrections[i]))
            rows.append(row)
            i += 1
        self.table = table.format("</tr><tr>".join(rows))
        if self.data.corrections == "":
            self.corrections_table = ""
        else:
            rows = self.data.corrections.split(";")
            data = []
            for row in rows:
                cells= ["<td>{}</td>".format(i) for i in row.split(":")]
                data.append("".join(cells))
            self.corrections_table = """<br />
                                        <p>Corrections:</p>
                                        <table>
                                            <tr><td>Input</td><td>Indicated</td></tr>""" + table.format("</tr><tr>".join(data)) + "</table>"
            
    def process(self):
        '''override if not using general'''
        self.get_data(data.general, self.id)
        self.extract_readings()
        self.calculate()
        self.uncertainty()
        self.generate_table()
    
    def generate_certificate(self):
        certificate= templates.get_template(self.template)
        self.process()
        outFile = open("{}\\certificates\\completed\\{}.html".format(DIR,
                                                     self.certificate_number),
                        "w")
        self.data.date = datetime.date(2016, 2, 22)
        due = self.data.date + datetime.timedelta(weeks=26)
        outFile.write(certificate.render(certificate_number=self.certificate_number,
                                         date=self.data.date.strftime("%d/%m/%Y"),
                                         by= self.calibrator,
                                         due= due.strftime("%d/%m/%Y"),
                                         customer=self.data.customer.upper(),
                                         type=self.data.name_of_instrument.upper(),
                                         manufacturer=self.data.manufacturer.upper(),
                                         serial=self.data.serial,
                                         range=self.data.range,
                                         units= self.data.units.upper(),
                                         resolution=self.data.resolution,
                                         location=self.data.location,
                                         temperature=self.temp,
                                         humidity=self.humidity,
                                         fields = self.table,
                                         standard = self.standard,
                                         corrections= self.corrections_table,
                                         uncertainty= self._uncertainty,
                                         traceability=self.traceability
                                         ))
        outFile.close()

class autoclave_certificate(certificate):    
        
    def extract_temp(self):
        temp_table = self.data.temp
        rows = temp_table.split(";")
        self.temp_actual = []
        self.temp_indicated = []
        for row in rows:
            cells = row.split(":")
            self.temp_actual.append(cells[0])
            self.temp_indicated.append(cells[1])
    
    def extract_pressure(self):
        pressure_table = self.data.pressure
        rows = pressure_table.split(";")
        self.p_applied = []
        self.p_calculated = []
        self.p_indicated = []
        
        for row in rows:
            cells = row.split(":")
            print(cells)
            self.p_applied.append(cells[0])
            self.p_calculated.append(cells[1])
            self.p_indicated.append(cells[2])
            
    def extract_readings(self):
        self.extract_pressure()
        self.extract_temp()
                
    def pressure_uncertainty(self):
        self.corrections = []
        for i in range(len(self.p_indicated)):
            self.corrections.append(abs(float(
                            self.p_indicated[i])- float(
                                        self.p_calculated[i])))
            
        squared = [math.pow(i, 2) for i in self.corrections]
        squared.append(math.pow(float(self.data.resolution_p), 2))
        self.uncertainty_p = "{:0.4f}".format(math.sqrt(sum(squared)))    
    
    
    def temp_uncertainty(self):
        self.temp_corrections = []
        for i in range(len(self.temp_indicated)):
            self.temp_corrections.append(abs(float(
                    self.temp_actual[i])-float(
                            self.temp_indicated[i]))) 
        squared = [math.pow(i, 2) for i in self.temp_corrections]
        squared.append(math.pow(float(self.data.resolution_temp), 2))
        self.uncertainty_temp="{:0.4f}".format(math.sqrt(sum(squared)))
        
    def uncertainty(self):
        self.pressure_uncertainty()
        self.temp_uncertainty()    
    
    def pressure_table(self):
        t = "<tr>{}</tr>"
        rows = []
        for i in range(len(self.p_applied)):
            rows.append("<td>{}</td><td>{}</td><td>{}</td><td>{:0.2f}</td>".format(
                      self.p_applied[i], self.p_calculated[i], self.p_indicated[i], 
                      self.corrections[i]))
        self.p_table = t.format("</tr><tr>".join(rows))
        
    def temp_table(self):
        rows = []
        t = "<tr>{}</tr>"
        for i in range(len(self.temp_indicated)):
            rows.append("<td>{}</td><td>{}</td><td>{}</td>".format(
                        self.temp_actual[i], self.temp_indicated[i], self.temp_corrections[i]))
    
        self.t_table = t.format("</tr><tr>".join(rows))

    def generate_table(self):
        self.temp_table()
        self.pressure_table()
        
    def process(self):
        self.get_data(data.autoclave, self.id)
        self.extract_readings()
        self.calculate()
        self.uncertainty()
        self.generate_table()
        
    def generate_certificate(self):
        certificate= templates.get_template("autoclave.html")
        self.process()
        outFile = open("{}\\certificates\\completed\\{}.html".format(DIR,
                                                     self.certificate_number),
                        "w")
        self.data.date = datetime.date(2016, 2, 22)
        due = self.data.date + datetime.timedelta(weeks=26)
        outFile.write(certificate.render(certificate_number=self.certificate_number,
                                         date=self.data.date.strftime("%d/%m/%Y"),
                                         by= self.calibrator,
                                         due= due.strftime("%d/%m/%Y"),
                                         customer=self.data.customer.upper(),
                                         type="AUTOCLAVE",
                                         manufacturer=self.data.manufacturer.upper(),
                                         serial=self.data.serial,
                                         range="{}({})".format(self.data.range_p,self.data.range_temp),
                                         units= "{}({})".format(self.data.units_p, self.data.units_temp),
                                         resolution="{}({})".format(self.data.resolution_p,
                                                                    self.data.resolution_temp),
                                         location=self.data.location,
                                         temperature=self.temp,
                                         humidity=self.humidity,
                                         fields = self.p_table,
                                         fields_temperature= self.t_table,
                                         uncertainty= self.uncertainty_p,
                                         uncertainty_temperature = self.uncertainty_temp  
                                         ))
        outFile.close()

        
        
class volume_certificate(certificate):
    def __init__(self, *args):
        super().__init__(*args)
        self.template = 'volume.html'

class conductivity_certificate(certificate):
    def __init__(self, *args):
        super().__init__(*args)
        self.template = "conductivity.html"
        
class current_certificate(certificate):
    def __init__(self, *args):
        super().__init__(*args)
        self.template = 'current.html'
    
    def generate_table(self):
        table = "<tr>{}</tr>"
        rows = []
        i= 0 
        while i < len(self.calculator_input):
            row = "<td>{:0.3f}</td><td>{:0.3f}</td><td>{:0.3f}</td><td>{:0.3f}</td><td>PASS</td>".format(self.calculator_input[i], 
                                                            self.indicated[i],
                                                            float(self.corrections[i]),
                                                            (math.sqrt(math.pow(float(self.corrections[i]), 2) *
                                                                        math.pow(float(self.data.resolution), 2))))
            rows.append(row)
            i += 1
        self.table = table.format("</tr><tr>".join(rows))
        
class voltage_certificate(current_certificate):
    def __init__(self, *args):
        super().__init__(*args)
        self.template = 'voltage.html'
        

        
class ph_certificate(certificate):
    def __init__(self, *args):
        super().__init__(*args)
        self.template = 'ph.html'
        
    def generate_table(self):
        table = "<tr>{}</tr>"
        print(self.corrections)
        rows = []
        i= 0 
        while i < len(self.calculator_input):
            row = "<td>{:0.1f}</td><td>{:0.1f}</td><td>{:0.4f}</td>".format(self.calculator_input[i], 
                                                            self.indicated[i],
                                                            float(self.corrections[i]))
            rows.append(row)
            i += 1
        self.table = table.format("</tr><tr>".join(rows))
        
class tds_certificate(certificate):
    def __init__(self, *args):
        super().__init__(*args)
        self.template = 'tds.html'
        
class flow_certificate(certificate):
    def __init__(self, *args):
        super().__init__(*args)
        self.template = 'flow.html'

class length_certificate(certificate):
    def __init__(self, *args):
        super().__init__(*args)
        self.template = 'length.html'
        
class temperature_certificate(certificate):
    def __init__(self, *args):
        super().__init__(*args)
        self.template = 'temperature.html'
        
class mass_certificate(certificate):
    def __init__(self, *args):
        super().__init__(*args)
        self.template = 'mass_pieces.html'
        
    """def get_data(self, table, id):
        this nction will parse the database and find all the masss pieces with the same'
        serial these will be differentiated using the serial:nominal syntax
        after these values are identified they are keyed in and a single table combining them
        all will be created
        self.associated = {}
        for i in data.session.query(data.general).filter("_type"="mass"):
            if i._id.split(":")[0] == id:
                self.associated[i._id.split(":")[1]] = i._id.split(":")[0]
        
        pass"""        
    
    def calculate(self):
        self.st = data.session.query(data.general_standards).get(self.data.standards)
        
        self.std_reading = []
        self.uut_reading = []
        self.uut_actual = []
        for i in self.data.readings.split(";"):
            row = i.split(":")
            self.std_reading.append(float(row[0]))
            self.uut_reading.append(float(row[1]))
            self.uut_actual.append(float(self.st.actual_values)- float(row[0]) + float(row[1]))
            
        self.uut_actual_mass = mean(self.uut_actual)
        self.dev = stdev(self.uut_actual)
    
    def uncertainty(self):
        r_factor=float(self.data.resolution)/ 2 
        res_factor = r_factor / math.sqrt(3)
        std_factor = 0.003 / 2
        normal_uncertainty = math.sqrt(
                        math.pow(res_factor, 2) + math.pow(
                                std_factor, 2) + math.pow(self.dev, 2))
         
        self._uncertainty = round((normal_uncertainty * 2), 6)
        
    def generate_table(self):
        table = """
                <table>
                    <tr>
                        <td>Actual Mass of standard</td>
                        <td>{}</td>
                        <td>Uncertainty of standard</td>
                        <td>{}</td>
                    </tr>
                </table>
                <br />
                <table>
                    <tr>
                        <td>Reading #</td>
                        <td>Standard Reading</td>
                        <td>UUT Reading</td>
                        <td>Actual Mass UUT</td>
                    </tr>
                    <tr>{}</tr>
                    <tr>
                        <td>Actual Mass of UUT</td>
                        <td>{}</td>
                        
                    </tr>
                    <tr>
                        <td>Standard deviation of readngs</td>
                        <td>{}</td>
                        
                    </tr>
                    <tr>
                        <td>Calculated Uncertainty +/-</td>
                        <td>{}</td>
                        
                    </tr>
                </table>"""
        rows = []        
        for i in range(len(self.std_reading)):
            rows.append("<td>{}</td><td>{}</td><td>{}</td><td>{}</td>".format(i+1, 
                                                                              self.std_reading[i],
                                                                              self.uut_reading[i],
                                                                              self.uut_actual[i]))
            
        self.table = table.format(self.st.actual_values,
                                  self.st.uncertainty,
                                  "</tr><tr>".join(rows),
                                  self.uut_actual_mass,
                                  self.dev,
                                  self._uncertainty)
        self.corrections_table = ""

if __name__=="__main__":
   pass