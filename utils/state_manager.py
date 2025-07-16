import os
import pandas as pd
from datetime import datetime

# ──────────────────────────────────────────────
# 1️⃣ Aplanar estado de sesión para exportación
# ──────────────────────────────────────────────

def flatten_session_state(d, parent_key='', sep='__'):
    """
    Aplana recursivamente un diccionario anidado (ej: st.session_state) para exportación en CSV o Google Sheets.

    - Convierte listas de diccionarios en JSON-like strings.
    - Convierte listas simples en cadenas separadas por comas.
    - Deja booleanos en su forma original (True/False), para restauración segura.

    Args:
        d (dict): Diccionario aplanar (ej: st.session_state).
        parent_key (str): Prefijo para claves anidadas.
        sep (str): Separador entre niveles de claves.

    Returns:
        dict: Diccionario plano listo para exportación.
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_session_state(v, new_key, sep=sep))
        elif isinstance(v, list):
            if all(isinstance(i, dict) for i in v):
                items[new_key] = str(v)
            else:
                items[new_key] = ", ".join(map(str, v))
        else:
            items[new_key] = v  # Conserva bool como bool
    return items



# ──────────────────────────────────────────────
# 2️⃣ Guardar respuestas en CSV (local)
# ──────────────────────────────────────────────

def save_response_to_csv(session_state, output_dir="data/responses"):
    """
    Guarda los datos del session_state en:
    1. Un archivo CSV único con marca de tiempo.
    2. Un archivo maestro acumulativo (responses_master.csv).

    Args:
        session_state (dict): Estado actual de la encuesta.
        output_dir (str): Carpeta donde se guardarán los archivos.

    Retorna:
        str: Ruta del archivo único generado.
    """
    os.makedirs(output_dir, exist_ok=True)

    flat_data = flatten_session_state(session_state)
    df = pd.DataFrame([flat_data])

    # Preparar nombre de archivo único
    ips_id = flat_data.get("identificacion__ips_id", "anonimo").replace(" ", "_").lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"BLH_{ips_id}_{timestamp}.csv"
    unique_path = os.path.join(output_dir, unique_filename)

    # Guardar archivo individual
    df.to_csv(unique_path, index=False)

    # Actualizar archivo maestro acumulativo
    master_path = os.path.join(output_dir, "responses_master.csv")
    if os.path.exists(master_path):
        df.to_csv(master_path, mode="a", header=False, index=False)
    else:
        df.to_csv(master_path, index=False)

    return unique_path


# ──────────────────────────────────────────────
# 3️⃣ Calcular progreso general del formulario
# ──────────────────────────────────────────────

def compute_progress(session_state, tracked_completion_flags):
    """
    Calcula el número de secciones completadas y el porcentaje de avance total.

    Args:
        session_state (dict): Estado de sesión actual (ej: st.session_state).
        tracked_completion_flags (list): Lista de claves de progreso (ej: ["datos_generales__completed", ...]).

    Retorna:
        tuple: (número de secciones completas, porcentaje de avance como entero)
    """
    if not tracked_completion_flags:
        return 0, 0

    completed_sections = sum(1 for flag in tracked_completion_flags if session_state.get(flag, False))
    percent_complete = int((completed_sections / len(tracked_completion_flags)) * 100)

    return completed_sections, percent_complete


# ──────────────────────────────────────────────
# 4️⃣ Verificar si sección está completa
# ──────────────────────────────────────────────

def is_section_completed(session_state, completion_flag):
    """
    Verifica si una sección específica está marcada como completada.

    Args:
        session_state (dict): Estado de sesión.
        completion_flag (str): Nombre de la clave de completitud (ej: 'personal_exclusivo__completed').

    Retorna:
        bool: True si está completada, False en caso contrario.
    """
    return bool(session_state.get(completion_flag, False))
