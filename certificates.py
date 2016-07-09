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


def min_max(ll):
    max = 0
    l = [float(i) for i in ll]
    for i in l:
        if i > max:
            max = i
            
    min = max
    for i in l:
        if i < min:
            min = i
    
    return (min, max)

def percent_difference(a, b):
    """returns the percentage difference between a and b where a is the 
    nominal value"""
    diff = abs(float(a)-float(b))
    r= (diff/ a) * 100
    print(r)
    return r 
    
def _round(n):
    r= int(n)
    if r < n:
        return r + 1
    else:
        return r
        
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
class balance_certificate():
    def __init__(self, _id, initials, by, temp, humidity):
        self.id = _id
        self.today = datetime.date.today()
        self.initials = initials
        self.temp= temp
        self.humidity = humidity
        self.certificate_number(self.initials)
        self.template = "balances.html"
        
        
    def certificate_number(self, initials):
        now = datetime.datetime.now()
        self.certificate_number= "{}{}".format(now.strftime("%Y%m%d%H%M"),
                               self.initials)
        
    def get_data(self):
        self.data = data.session.query(data.balance).get(self.id)
        self.tare = data.session.query(data.balance_tare).get(self.id)
        self.linearity_before = data.session.query(data.balance_before_calibration).get(self.id)
        self.linearity_after = data.session.query(data.balance_linearity_after).get(self.id)
        self.off = data.session.query(data.balance_off_center).get(self.id)
        self.repeatability = data.session.query(data.balance_repeatability).get(self.id)
        self.standard = data.session.query(data.general_standards).get(self.data.standard)
        
    def process(self):
        self.get_data()
        self.repeatability_table()
        self.uncertainty()

        
    def uncertainty(self):
        stds_uncertainty = [float(i) for i in self.standard.uncertainty.split("|")]
        def sqsqrt(l):
            squares = [math.pow(i, 2) for i in l]
            return math.sqrt(sum(squares))
        
        standard_u_contrib = sqsqrt(stds_uncertainty)
        res_contrib =  (float(self.data.resolution) / 2 ) / math.sqrt(3)
        drift_contrib = abs(self.cold_drift()) / math.sqrt(3)    
        repeat_contrib = sqsqrt(self.deviation)
        
        self._uncertainty = round(sqsqrt([standard_u_contrib,
                                   res_contrib,
                                   drift_contrib,
                                   repeat_contrib]) * 2, 6)
    def settling_average(self):
        settling = self.data.settling_time.split(":")
        settling = [float(i) for i in settling]
        total = 0
        for i in settling:
            total += i
            
        return round((total / len(settling)), 6)
    
    def off_max_error(self):
        '''maximum corner errors'''
        tab= [self.off.a, self.off.b, self.off.c, self.off.d, self.off.e]    
        return min_max(tab)
		
		
    def cold_drift(self):
        '''the total cold start readings
        average of maximum and minimum values
        test_weight value - ((max + min)/2) '''
        cold_values = self.data.nominal_mass.split(":")
        extremes = min_max(cold_values)
        return round(float(self.data.warm_up_nominal) - ((extremes[0] + extremes[1]) / 2), 6)
        
    def nominal_table(self):
        nominal = self.linearity_before.nominal_value.split(":")
        act = self.standard.actual_values.split("|")
        stdnom = self.standard.nominal_values.split("|")
        actual = []
        for i in nominal:
            indx = stdnom.index(i)
            actual.append(float(act[indx]))
            
        lin_up = self.linearity_before.linearity_up.split(":")
		
        
        differences = []
        l = 0
        while l < len(actual):
            differences.append(abs(actual[l]-float(lin_up[l])))
            l += 1 
		
        table = """<table>
					{}{}{}{}
					<tr>
						<td>Calibration Adjustment Effected</td>
						<td></td>
					</tr>
					<tr>
						<td>Weights used for correction</td>
						<td></td>
					</tr>
		</table>"""
		
        actual = [str(i) for i in actual]
        nom_row = "<tr><td>Nominal Mass</td><td>{}</td></tr>".format("</td><td>".join(nominal))
        act_row = "<tr><td>Actual Mass</td><td>{}</td></tr>".format("</td><td>".join(actual))
        lin_row = "<tr><td>Linearity Up</td><td>{}</td></tr>".format("</td><td>".join(lin_up))
        dlist = []
        for i in differences:
            dlist.append("<td>{0:0.6f}</td>".format(i))
            
        dlist = [str(i) for i in dlist] 
        dif_row = "<tr><td>Difference</td>{}</tr>".format("".join(dlist))
		
        return table.format(nom_row, act_row, lin_row, dif_row)
	
    def standards_table(self):
        table = """<table>
						<tr>
							<td>Description</td>
							<td>Certificate Number</td>
							<td>Acutal Weight</td>
							<td>Uncertainty</td>
						</tr>
						{}
					</table>"""

        nom = self.standard.nominal_values.split("|")
        certificate = self.standard.certificate
        actual = self.standard.actual_values.split("|")
        uncertainty = self.standard.uncertainty.split("|")
        i = 0
        fields = []
        while i < len(actual):
            fields.append("""<tr>
								<td>{}</td>
								<td>{}</td>
								<td>{}</td>
								<td>{}</td>
							</tr>""".format(nom[i], certificate, actual[i], uncertainty[i]))
            i +=1 
		
        return table.format("".join(fields))
			
    def cold_start_table(self):
        
        table = """<table>
					<tr>
						<td>Test weight</td>
						<td>{}</td>
					</tr>
					<tr>
						<td>Test #</td>
						<td>Result</td>
					</tr>
					{}
					<tr>
						<td>Drift</td>
						<td>{}</td>
					</tr>
		</table>"""

        test_weight = self.data.warm_up_nominal
        cold_values = self.data.nominal_mass.split(":")
        i = 0
        fields = []
        while i < len(cold_values):
            fields.append("<tr><td>{}</td><td>{}</td></tr>".format(i + 1, cold_values[i]))
            i += 1

        return table.format(test_weight, "".join(fields), self.cold_drift())
			
    def settling_table(self):
        
        table = """<table>
						<tr>
							<td>Reading</td>
							<td>1st</td>
							<td>2nd</td>
							<td>3rd</td>
							<td>4th</td>
							<td>5th</td>
						</tr>
						<tr>
							<td>Settling Time</td>
							<td>{}</td>
						</tr>
						<tr>
							<td>Average Settling Time</td>
							<td>{}</td>
						</tr>
					</table>"""
					
        readings = self.data.settling_time.split(":")
        return table.format("</td><td>".join(readings), self.settling_average())
		
    def linearity_table(self):
            
        table = """<table>
					<tr>
						<td>Nominal Value</td><td>{}</td>
					</tr>
					<tr>
						<td>Actual Value</td><td>{}</td>
					</tr>
					<tr>
						<td>Linearity Up</td><td>{}</td>
					</tr>
					<tr>
						<td>Linearity Down</td><td>{}</td>
					</tr>
					<tr>
						<td>Linearity Up</td><td>{}</td>
					</tr>
					<tr>
						<td>Average Reading</td><td>{}</td>
					</tr>
					<tr>
						<td>Difference</td><td>{}</td>
					</tr>
					<tr>
						<td>Standard Deviation</td><td>{}</td>
					</tr>
					<tr>
						<td>Maximum Difference</td><td>{:0.6f}</td>
					</tr>
						
		</table>"""
        
        def get_nominals(self):
            nom_list = []
            act_list = []
            lin_list =[float(i) for i in self.linearity_after.linearity_up.split(":")]
            std_nom = [float(i) for i in self.standard.nominal_values.split("|")]
            std_act = [float(i) for i in self.standard.actual_values.split("|")]
            for i in std_nom:
                for j in lin_list:
                    if percent_difference(i, j) < 1:
                        
                        nom_list.append(i)
                        p = std_act[std_nom.index(i)]
                        act_list.append(p)
            return nom_list, act_list
        
        nom_list, act_list = get_nominals(self)
                    
        lin_up_list = [float(i) for i in self.linearity_after.linearity_up.split(":")]
        lin_uup_list = [float(i) for i in self.linearity_after.linearity_uup.split(":")]
        lin_down_list = [float(i) for i in self.linearity_after.linearity_Down.split(":")]
        average_list = []
        difference_list = []
        # sort values
        nom_list.sort()
        act_list.sort()
        lin_up_list.sort()
        lin_down_list.sort()
        lin_uup_list.sort()
        
        
        deviation_list = []
        p= 0
        while p < len(act_list):
            average_list.append((lin_down_list[p] + lin_up_list[p] + lin_uup_list[p]) / 3)
            difference_list.append(abs(act_list[p]- average_list[p]))
            deviation_list.append(stdev([lin_down_list[p], lin_up_list[p], lin_uup_list[p]]))
            p += 1 
            
        nom_list = [str(i) for i in nom_list]
        act_list = [str(i) for i in act_list]
        lin_up_list = [str(i) for i in lin_up_list]
        lin_uup_list = [str(i) for i in lin_uup_list]
        lin_down_list = [str(i) for i in lin_down_list]
        average_list = ["{0:0.6f}".format(i) for i in average_list]
        difference_list = ["{0:0.6f}".format(i) for i in difference_list]
        deviation_list = ["{0:0.6f}".format(i) for i in deviation_list]
        return table.format("</td><td>".join(nom_list),
                            "</td><td>".join(act_list),
                            "</td><td>".join(lin_up_list),
                            "</td><td>".join(lin_down_list),
                            "</td><td>".join(lin_uup_list),
                            "</td><td>".join(average_list),
                            "</td><td>".join(difference_list),
                            "</td><td>".join(deviation_list),
                            min_max(difference_list)[1])

    def repeatability_table(self):
        table = """<table>
                        <tr>
                            <td></td>
                            <td>1/2 Load</td>
                            <td>Full Load</td>
                        </tr>
                        <tr>
                            <td>Nominal Mass</td>
                            <td>{}</td>
                        </tr>
                        <tr>
                            <td>Actual Mass</td>
                            <td>{}</td>
                        </tr>
                        {}
                        <tr>
                            <td>Average Reading</td>
                            <td>{:0.6f}</td>
                            <td>{:0.6f}</td>
                        </tr>
                        <tr>
                            <td>Standard Deviaton</td>
                            <td>{:0.6f}</td>
                            <td>{:0.6f}</td> 
                        </tr>
                    </table>"""
                    
        half_list =[float(i) for i in self.repeatability.half_reading.split(":")]
        full_list =[float(i) for i in self.repeatability.full_reading.split(":")]
        rows = []
        i = 0
        while i < len(half_list):
            s = "<tr><td>Reading # {}</td><td>{}</td><td>{}</td></tr>"
            rows.append(s.format(i +1, half_list[i], full_list[i]))
            i += 1
            
        actual_values = []
        t = [half_list[0], full_list[0]]
        n = self.standard.nominal_values.split("|")
        nominal_values = []
        for i in n:
            for j in t:
                print(i, " ", j)
                if percent_difference(float(i), float(j)) < 1:
                    nominal_values.append(i)
                    actual_values.append(self.standard.actual_values.split("|")[n.index(i)])
        
        
        nominal_values.sort()
        actual_values.sort()
        
            
            
        nominal_values=[str(i) for i in nominal_values]
        self.deviation = [round(stdev(half_list), 6), round(stdev(full_list), 6)]
        return table.format("</td><td>".join(nominal_values),
                            "</td><td>".join(actual_values),
                            "\n".join(rows),
                            mean(half_list),
                            mean(full_list),
                            stdev(half_list),
                            stdev(full_list))
        
    def off_center_table(self):
        table = """<table>
                        <tr>
                            <td>Test Weight</td>
                            <td>{}</td>
                        </tr>
                        <tr>
                            <td>Position</td>
                            <td>Reading</td>
                            <td>Weight Difference</td>
                        </tr>
                        {}
                        <tr>
                            <td>Minimum Reading</td>
                            <td>{}</td>
                        </tr>
                        <tr>
                            <td>Maximum Reading</td>
                            <td>{}</td>
                        </tr>
                        <tr>
                            <td>Average Reading</td>
                            <td>{}</td>
                        </tr>
                        <tr>
                            <td>Minimum Corner Error</td>
                            <td>{}</td>
                        </tr>
                        <tr>
                            <td>Standard Deviation of Readings</td>
                            <td>{:0.6f}</td>
                        </tr>
                    </table>"""
    
        test_weight = float(self.data.off_center_mass)
        positions = ["A","B","C","D","E"]
        r = [self.off.a, self.off.b, self.off.c, self.off.d, self.off.e]
        readings = [float(i) for i in r]
        differences = [abs(test_weight - i ) for i in readings ]
        i = 0
        rows = []
        while i < len(positions):
            rows.append("<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(positions[i], 
                                                                            readings[i],
                                                                            differences[i]))
            i += 1
        
        return table.format(test_weight,
                            "\n".join(rows),
                            min_max(readings)[0],
                            min_max(readings)[1],
                            mean(readings),
                            abs(min_max(differences)[0]- test_weight),
                            stdev(readings))
        
    def generate_certificate(self):
        certificate= templates.get_template(self.template)
        self.process()
        outFile = open("{}\\certificates\\completed\\{}.html".format(DIR,
                                                     self.certificate_number),
                        "w")
        
        outFile.write(certificate.render(certificate_number=self.certificate_number,
                                         date=self.today.strftime("%d/%m/%Y"),
                                         customer=self.data.customer.upper(),
                                         type= "BALANCE",
                                         manufacturer=self.data.manufacturer.upper(),
                                         serial=self.data.serial,
                                         model = self.data.model.upper(),
                                         range=self.data.range,
                                         resolution=self.data.resolution,
                                         location=self.data.location,
                                         #
                                         # results
                                         #
                                         settling_average=self.settling_average(),
                                         corner = self.data.off_center_mass,
                                         corner_error= self.off_max_error()[1],
                                         drift = self.cold_drift(),
                                         half_repeat = round(self.deviation[0], 6),
                                         full_repeat = round(self.deviation[1], 6),
                                         #
                                         # tables
                                         #
                                         nominal_table = self.nominal_table(),
                                         standards_table= self.standards_table(),
                                         cold_start_table= self.cold_start_table(),
                                         settling_table= self.settling_table(),
                                         repeatability_table= self.repeatability_table(),
                                         off_table= self.off_center_table(),
                                         linearity_table = self.linearity_table(),
                                         #
                                         # procedure
                                         #
                                         procedure= self.data.procedure,
                                         temperature=self.temp,
                                         humidity=self.humidity,
                                         units= self.data.units.upper(),
                                         #
                                         # template
                                         #
                                         uncertainty= self._uncertainty
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
         
class length_certificate(certificate):
    def __init__(self, *args):
        super().__init__(*args)
        self.template = 'length.html'
        
    

class temperature_certificate(certificate):
    def __init__(self, *args):
        super().__init__(*args)
        self.template = 'temperature.html'    
        
    


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
        

if __name__=="__main__":
   """f = tds_certificate("63128", "CK", "Caleb Kandoro", "30", "40" )
   f.generate_certificate()
   
   f = volume_certificate("18135", "CK", "Caleb Kandoro")
   f.generate_certificate()
   
   f = current_certificate("32327", "CK", "Caleb Kandoro")
   f.generate_certificate()
   
   f = flow_certificate("41923", "CK", "Caleb Kandoro")
   f.generate_certificate()
   
   f = voltage_certificate("58802", "CK", "Caleb Kandoro")
   f.generate_certificate()
   
   f = pressure_certificate("77828", "CK", "Caleb Kandoro")
   f.generate_certificate()
   
   f = mass_certificate("test_mass", "CK", "Caleb Kandoro", "28", "45")
   f.generate_certificate()
   
   f = temperature_certificate("90358", "CK", "Caleb Kandoro")
   f.generate_certificate()
   
   f = ph_certificate("97938", "CK", "Caleb Kandoro")
   f.generate_certificate()
   
   f = conductivity_certificate("98557", "CK", "Caleb Kandoro")
   f.generate_certificate()
   
   f = length_certificate("27711", "CK", "Caleb Kandoro")
   f.generate_certificate()
   
   f = autoclave_certificate("14062016a123", "CK", "Caleb Kandoro", "27", "50")
   f.generate_certificate()
   """
   f = balance_certificate("1606166A7601332", "KK", "27", "45")
   f.generate_certificate()