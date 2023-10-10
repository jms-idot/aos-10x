def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    
def sanitize_field(value):
    if value.isnumeric():
        return int(value)
    elif is_float(value):
        return float(value)
    return value