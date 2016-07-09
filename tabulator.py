'''
Created on Apr 20, 2016

@author: caleb kandoro
'''
import data
def horizontal_tabulation(reading, row,headings=[], session={}):
    '''takes one reading at a time and appends it to the end of the appropriate row'''
    row = int(row)
    table_string = """<table>
                {}
            </table"""
            
    if "table" not in session: #makes sure a table session dictionary exists
        session["table"] = {}
        table = session["table"] # a simpler variable for use in the fucntion
        i = 0
        for heading in headings:
            table[heading] = [] # instantiate the lists
            i += 1 #i is used to traverse fields
        table[headings[row]].append(str(reading)) # creates the first value in the row
    else:
        table = session["table"]
        table[headings[row]].append(str(reading)) #adds the reading to the appropriate row
            
    print(table)
                
    i = 0
    row_strings = []
    for heading in headings:
            r= "<tr><td>{}</td>".format(heading)
            if len(table[headings[i]]) > 0:
                cells = []
                for item in table[headings[i]]:
                    cells.append("<td>{}</td>".format(item))
                    
                row_strings.append(r + "".join(cells) + "</tr>")
            
            else:
                row_strings.append(r + "</tr>")
            i += 1
    return table_string.format("".join(row_strings))
        

def general_tabulation( fields = [], session = {}, headings =[], numbered=False):
    """general function for creating tables based on lists of fields and 
        a variable number of arguments""" 
    
    
    if len(fields) != len(headings):
        return "this table wont work"
    
    if "table" not in session: #makes sure a table session dictionary exists
        session["table"] = {}
        table = session["table"] # a simpler variable for use in the fucntion
        i = 0
        for heading in headings:
            table[heading] = [fields[i]] # instantiate the appropriate values in the lists
            i += 1 #i is used to traverse fields
    else:
        i = 0
        table = session["table"]
        for heading in headings:
            table[heading].append(fields[i])
            i += 1
        
            
        
    response = """<table>
                        <tr>{}</tr>
                            {}
                            </table>
        """
        
    th = []
    if numbered:
        th.append("<th>Reading #</th>")
    for i in headings:
            th.append("<th>{}</th>".format(i))
            
        #creates a list of key valu pairs in the fields dictionary
    rows = []
    
    
    length = len(table[headings[0]])
    for i in range(length):
        row = []
        if numbered:
            row.append("<td>{}</td>".format(i +1))
        for heading in headings:
            row.append("<td>{}</td>".format(table[heading][i]))
        rows.append("<tr>" + "".join(row) + "</tr>")
        
    return response.format("".join(th), "".join(rows))
    
    
    
general_tabulation(fields = [50, 100, 23], headings=["actual", "indicated", "missions"])


def readings_formatter(args):
    length = len(args[0])
    print(args)
    l = 0
    table = []
    while l < length:
        row = []
        for i in args:
            print(i)
            row.append(i[l])
            print(row)
        table.append(":".join(row))
        l += 1
        
    return ";".join(table)

#readings_formatter(['1','2','3'], ['4','5','6'])

table= {"tare": ['1','2','3'],
         "repeat": ['1','2','3']}

_keys = table.keys()
_args= []
for key in _keys:
    try:
        _args.append(table[key])
    except:
        print("something went wrong")
    
#readings_formatter(_args)


def get_initials(user):
    name= data.session.query(data.users).get(user)
    try:
        _name= name.full_name.split(" ")
        return "".join([_name[0][0], _name[1][0]]).upper()
    except:
        return name.full_name[0].upper()
def calculate_pressure_psi(weight):
    weight = float(weight)
    return (weight/45.19)+5.0150254481


def calculate_pressure_bar(weight):
    weight = float(weight)
    return calculate_pressure_psi(weight) / 14.5038
    

        
def calculate_pressure_kpa(weight):
    weight = float(weight)
    return calculate_pressure_bar(weight) * 100
    
def calculate_pressure_mpa(weight):
    val = calculate_pressure_bar(weight) / 10
    return val
    
def calculate_pressure_pa(weight):
    return calculate_pressure_bar(weight) / 100000
