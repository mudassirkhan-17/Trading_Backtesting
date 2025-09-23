"""
Comparison Functions Module
Handles all comparison operations for trading strategy conditions
"""

def crossed_up(data, col1, col2):
    """Check if col1 crossed up above col2"""
    return (data[col1].shift(1) < data[col2].shift(1)) & (data[col1] > data[col2])

def crossed_down(data, col1, col2):
    """Check if col1 crossed down below col2"""
    return (data[col1].shift(1) > data[col2].shift(1)) & (data[col1] < data[col2])

def equal_comparison(data, col1, col2):
    """Check if col1 equals col2"""
    return abs(data[col1] - data[col2]) < 0.01

def greater_than(data, col1, col2):
    """Check if col1 is greater than col2"""
    return data[col1] > data[col2]

def greater_or_equal(data, col1, col2):
    """Check if col1 is greater than or equal to col2"""
    return data[col1] >= data[col2]

def less_than(data, col1, col2):
    """Check if col1 is less than col2"""
    return data[col1] < data[col2]

def less_or_equal(data, col1, col2):
    """Check if col1 is less than or equal to col2"""
    return data[col1] <= data[col2]

def within_range(data, col1, col2, tolerance=0.01):
    """Check if col1 is within range of col2"""
    return abs(data[col1] - data[col2]) <= tolerance

def increased(data, col1, col2):
    """Check if col1 increased from previous value"""
    return data[col1] > data[col1].shift(1)

def decreased(data, col1, col2):
    """Check if col1 decreased from previous value"""
    return data[col1] < data[col1].shift(1)

def crossed(data, col1, col2):
    """Check if col1 crossed col2 (either direction)"""
    return ((data[col1].shift(1) < data[col2].shift(1)) & (data[col1] > data[col2])) | \
           ((data[col1].shift(1) > data[col2].shift(1)) & (data[col1] < data[col2]))
