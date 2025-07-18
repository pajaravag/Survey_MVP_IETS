# utils/forms/validators.py

def safe_int(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    try:
        return float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return default

