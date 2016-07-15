from certificates import certificate
import data
from tabulator import general_tabulation, horizontal_tabulation
import datetime 
import time
import jinja2
import os

class pressure_certificate(certificate):
    def __init__(self, *args):
        super().__init__(*args)
        self.template = "pressure.html"
        
    def extract_readings(self):
        '''each table has a readings string may be able to generalize 
        it with time, but for now stick with individual implementations
        each implementation interface must take a set of input readings 
        extracted and place them in the self.calculator_input list whether 
        or not the input is going to be modified'''
        table = self.data.readings
        rows = table.split(";")
        self.indicated = []
        self.calculator_input = []
        for row in rows:
            print(row)
            cells = row.split(":")
            self.indicated.append(float(cells[2]))
            try:
                self.calculator_input.append(float(cells[0]))
            except:
                self.calculator_input.append(0.0)
            
    def calculate_pressure_bar(self, weight):
        weight = float(weight)
        return self.calculate_pressure_psi(weight) / 14.5038
    
    def calculate_pressure_psi(self, weight):
        weight = float(weight)
        return (weight/45.19)+5.0150254481
        
    def calculate_pressure_kpa(self, weight):
        weight = float(weight)
        return self.calculate_pressure_bar( weight) * 100
    
    def calculate_pressure_mpa(self, weight):
         val = self.calculate_pressure_bar(weight) / 100
         return val
     
    def calculate_pressure_pa(self, weight):
        val =  self.calculate_pressure_bar(weight) * 100000 
        return val
    
    def calculate(self):
        _units = {"bar": self.calculate_pressure_bar,
                     "psi": self.calculate_pressure_psi,
                     "kpa" :self.calculate_pressure_kpa,
                     "mpa": self.calculate_pressure_mpa,
                     "pa": self.calculate_pressure_pa}
            
        zero = {"bar": 0.3457732, 
                    "psi": 5.015025,
                    "kpa": 34.57732,
                    "pa": 34577.32,
                    "mpa": 0.03457732}
        i = 0
        while i < len(self.calculator_input):
            if i == 0 and self.calculator_input[i] == 0:
                #calculate the mass of the tray
                self.calculator_output.append(0)
            elif i == 1:
                if self.calculator_input[i] == 0:
                    self.calculator_output.append(zero[self.data.units.lower()])
                else:
                    self.calculator_output.append(_units[self.data.units.lower()](self.calculator_input[i]))
            else:
                    self.calculator_output.append(_units[self.data.units.lower()](self.calculator_input[i]))
            i += 1
        
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
    
        self._uncertainty = "{:0.4f}".format(math.sqrt(math.pow(float(self.data.resolution), 2) +
                                     math.pow(largest_difference, 2)
                                     ))
     
    def generate_table(self):
        table = "<tr>{}</tr>"
        rows = []
        i= 0 
        rows = self.data.readings.split(";")
        for i in range(len(rows)):
            r= rows[i].split(":")
            row = "<td>{}</td><td>{}</td><td>{}</td><td>{:0.2f}</td>".format(r[0],
                                                                                       r[1],
                                                                                       r[2],
                                                                                       self.corrections[i])
            rows.append(row)
            
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
                                            <tr><td>Applied Mass</td><td>Calculated</td><td>Indicated</td></tr>""" + table.format("</tr><tr>".join(data)) + "</table>"
        