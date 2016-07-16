def percent_difference(a, b):
    """function used in balance certificates to find the closest nominal value to a given value"""
    _sum = a-b
    _average = (a + b) / 2
    return (_sum / _average) * 100 


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