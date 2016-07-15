def percent_difference(a, b):
    """function used in balance certificates to find the closest nominal value to a given value"""
    _sum = a-b
    _average = (a + b) / 2
    return (_sum / _average) * 100 