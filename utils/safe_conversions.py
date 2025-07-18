# utils/safe_conversions.py

def safe_int(value, default=0):
    """
    Convierte un valor a entero de forma segura.
    Si no se puede convertir, retorna el valor por defecto.
    """
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """
    Convierte un valor a float de forma segura.
    Soporta coma como separador decimal.
    Si no se puede convertir, retorna el valor por defecto.
    """
    try:
        return float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return default
