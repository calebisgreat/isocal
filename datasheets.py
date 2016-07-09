from jinja2 import Environment, Template 
import jinja2
import data
import os
import datetime
import time
ROOTDIR = os.path.abspath(os.getcwd())

class general_datasheet():
    
    def __init__(self, id, user):
        self.id = id
        self.user = user
        self.templates = Environment(loader=jinja2.FileSystemLoader(os.path.join(ROOTDIR,"certificates\\templates"))) 
    
    def generate_datasheet(self):
        self.get_data()
        datasheet= self.templates.get_template("general_datasheet.html")
        try:
            s = time.strftime("%H:%M",time.localtime(float(self.data.start_time)))
            e = time.strftime("%H:%M",time.localtime(float(self.data.end_time)))
        except:
            s= self.data.start_time
            e=self.data.end_time
        try:
            fil=open(os.path.join(ROOTDIR, "certificates\\datasheets\\{}.html".format(self.id)), "w")
        except:
            fil=open(os.path.join(ROOTDIR, "certificates\\datasheets\\{}.html".format(self.data.name_of_instrument)), "w")
        
        fil.write(datasheet.render(customer=self.data.customer,
                                   number= datetime.datetime.now().strftime("%y%m%d%H%M%S") + self.user,
                                   address=self.data.location,
                                   date=self.data.date,
                                   manufacturer=self.data.manufacturer,
                                   user=self.user,
                                   name=self.data.name_of_instrument,
                                   model=self.data.model,
                                   standards=self.data.standards,
                                   serial=self.data.serial,
                                   range=self.data.range,
                                   immersion=self.data.immersion_depth,
                                   resolution=self.data.resolution,
                                   unit=self.data.units,
                                   start_time=s,
                                   end_time=e,
                                   readings=self.generate_table(),
                                   comments=self.data.comments
                                   ))
        fil.close()
        
        
    def get_data(self):
        self.data = data.session.query(data.general).get(self.id)
        
    def generate_table(self):
        rows = self.data.readings.split(";")
        result = "<tr>"
        for row in rows:
            r=row.split(":")
            for i in r:
                result += "<td>" + i + "</td>"
                
            result += "</tr><tr>"
        result += "</tr>"
        return result

class balance_datasheet():
    def __init__(self, id, user):
        self.id =id
        self.user = user
        self.data = data.session.query(data.balance).get(self.id)
        self.lin = data.session.query(data.balance_before_calibration).get(self.id)
        self.lin_two = data.session.query(data.balance_linearity_after).get(self.id)
        self.tare = data.session.query(data.balance_tare).get(self.id)
        self.repeat = data.session.query(data.balance_repeatability).get(self.id)
        self.off = data.session.query(data.balance_off_center).get(self.id)
        self.templates = Environment(loader=jinja2.FileSystemLoader(os.path.join(ROOTDIR,"certificates\\templates")))
        
    def generate_datasheet(self):
        cert = self.templates.get_template("balance_datasheet.html")
        fil = open(os.path.join(ROOTDIR, "certificates\\datasheets\\{}.html".format(self.id)), "w")
        fil.write(cert.render(date =self.data.date,
                              customer=self.data.customer,
                              name_of_instrument="Balance",
                              manufacturer=self.data.manufacturer,
                              model=self.data.model,
                              serial=self.data.serial,
                              range=self.data.range,
                              resolution=self.data.resolution,
                              units=self.data.units,
                              location=self.data.location,
                              user=self.user,
                              number=datetime.datetime.now().strftime("%y%m%d%H%M%S") + self.user,
                              procedure= self.data.procedure,
                              nominal_values=self.create_cells(self.data.nominal_mass),
                              settling_values=self.create_cells(self.data.settling_time),
                              lin_nominal_values=self.create_cells(self.lin.nominal_value),
                              lin_actual="<td></td><td></td><td></td><td></td><td></td>",
                              lin_linearity_up=self.create_cells(self.lin.linearity_up),
                              _2_lin_up= self.create_cells(self.lin_two.linearity_up),
                              _2_lin_down=self.create_cells(self.lin_two.linearity_Down),
                              _2_lin_up_2=self.create_cells(self.lin_two.linearity_uup),
                              _tare_values=self.create_cells(self.tare.tare),
                              tare_indicated=self.create_cells(self.tare.indicated),
                              half_values=self.create_cells(self.repeat.half_reading),
                              full_values=self.create_cells(self.repeat.full_reading),
                              off_center=self.off_center_table()
                              ))
        fil.close
        
    def create_cells(self, data):
        result = ""
        for i in data.split(":"):
            result += "<td>" + i + "</td>"
            
        return result
    
    def off_center_table(self):
        return """<tr>
                    <td>A</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td>B</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td>C</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td>D</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td>E</td>
                    <td>{}</td>
                </tr>""".format(self.off.a, self.off.b,
                                self.off.c, self.off.d,
                                self.off.e)

if __name__ == "__main__":
    d=general_datasheet("3105161827231012", 'KK')
    d.generate_datasheet()
    
