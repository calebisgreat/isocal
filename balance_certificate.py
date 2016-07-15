from utilities import percent_difference
import datetime
import data
from tabulator import general_tabulation, horizontal_tabulation
import time
import jinja2
import os
import math
from statistics import stdev, mean
from builtins import round
"""balance certificate structure:

"""
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
        self.certificate_number= "{}{}".format(now.strftime("%Y%m%d%H%M%S"),
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
        """overall uncertainty of the data derived from the uncertainty of the standards, the measurements
        drift, repeatbility """
        
        stds_uncertainty = [float(i) for i in self.standard.uncertainty.split("|")]
        def squareroot_of_sum_of_squares(l):
            squares = [math.pow(i, 2) for i in l]
            return math.sqrt(sum(squares))
        
        standard_u_contrib = squareroot_of_sum_of_squares(stds_uncertainty)
        res_contrib =  (float(self.data.resolution) / 2 ) / math.sqrt(3)
        drift_contrib = abs(self.cold_drift()) / math.sqrt(3)    
        repeat_contrib = squareroot_of_sum_of_squares(self.deviation)
        
        self._uncertainty = round(squareroot_of_sum_of_squares([standard_u_contrib,
                                   res_contrib,
                                   drift_contrib,
                                   repeat_contrib]) * 2, 6)
    
    def settling_average(self):
        """used to fill the field of the settling table regarding average time"""
        settling = self.data.settling_time.split(":")
        settling = [float(i) for i in settling]
        return round(mean(settling), 6)
    
    def off_max_error(self):
        '''maximum corner errors'''
        return max([self.off.a, self.off.b, self.off.c, self.off.d, self.off.e])    
        
    def cold_drift(self):
        '''the total cold start readings
        average of maximum and minimum values
        test_weight value - ((max + min)/2) '''
        cold_values = self.data.nominal_mass.split(":")
        average_over_span = (min(cold_values) + max(cold_values)) / 2
        return round(float(self.data.warm_up_nominal) - average_over_span, 6)
        
    def nominal_table(self):
        """due to adjustments in the recording from the app much of 
        the extrapolation of nominal values may well be unneccessary""""
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
                            max(difference_list))

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
                            min(readings),
                            max(readings),
                            mean(readings),
                            abs(min(differences)- test_weight),
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