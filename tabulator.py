'''
Created on Apr 20, 2016

@author: caleb kandoro
'''
import data

def create_row(data):   
    if len(data) == 1:
        return "<tr><td>" + data + "</td></tr>\n"
    else:
        return "<tr><td>{}</td></tr>\n".format("</td>\n<td>".join(data))
    
def simple_table(data = {}, fields= [], horizontal=False):
    table_string = "<table>{}\n</table>"
    rows =[]
    if horizontal:
        for field in fields:
            row = [field]
            row += data[field]
            rows.append(create_row(row))
            
    else:
        rows.append(create_row(fields))
        for i in range(len(data[fields[0]])):
            #select the i element in each field
            #add them to a list
            row_data = [data[field][i] for field in fields] 
            rows.append(create_row(row_data))
            
        
            
    return table_string.format("".join(rows))

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


table= {"tare": ['1','2','3'],
         "repeat": ['1','2','3']}

print(simple_table(table, ["tare", "repeat"])) 
    



