import streamlit as st
import json
from datetime import datetime
from typing import Callable, Optional, Tuple, List, Dict, Any
from utils.constants import MINIMUM_HEADERS_BY_SECTION
from utils.sheet_io import load_existing_data

# ───────────────────────────────────────────────────────────────────────────────
# 🔧 Aplanar el estado de sesión en un diccionario plano por prefijo
# ───────────────────────────────────────────────────────────────────────────────
def flatten_session_state(
    session_state: Optional[Dict[str, Any]] = None,
    prefix: Optional[str] = None
) -> Dict[str, Any]:
    session_state = session_state or st.session_state

    def is_scalar(val):
        return isinstance(val, (str, int, float, bool)) or val is None

    if prefix:
        if not prefix.endswith("__"):
            prefix += "__"
        filtered = {
            k[len(prefix):]: v
            for k, v in session_state.items()
            if k.startswith(prefix) and k != prefix and is_scalar(v) and v not in ("", None, [], {})
        }
    else:
        filtered = {
            k: v
            for k, v in session_state.items()
            if is_scalar(v) and v not in ("", None, [], {})
        }
    return filtered

# ───────────────────────────────────────────────────────────────────────────────
# 🕒 Marcar el momento en que se inicia una sección del formulario
# ───────────────────────────────────────────────────────────────────────────────
def register_section_timestamp(prefix: str) -> None:
    if not prefix.endswith("__"):
        prefix += "__"
    key = f"{prefix}section_started_at"
    if key not in st.session_state:
        st.session_state[key] = datetime.now().isoformat()

# ───────────────────────────────────────────────────────────────────────────────
# 🧼 Extraer encabezados del estado de sesión por prefijo
# ───────────────────────────────────────────────────────────────────────────────
def extract_headers_from_session(prefix: str) -> List[str]:
    if not prefix.endswith("__"):
        prefix += "__"
    headers = [k for k in st.session_state if k.startswith(prefix)]
    if not headers:
        headers = MINIMUM_HEADERS_BY_SECTION.get(prefix, [])
    return sorted(headers)

# ───────────────────────────────────────────────────────────────────────────────
# 💾 Guardado seguro de una sección del formulario
# ───────────────────────────────────────────────────────────────────────────────
def safe_save_section(
    section_prefix: str,
    id_field: str,
    sheet_name: str,
    save_func: Optional[Callable[[str, str, str], None]] = None
) -> None:
    if not section_prefix.endswith("__"):
        section_prefix += "__"

    register_section_timestamp(section_prefix)

    if save_func is None:
        from utils.sheet_io import save_section_to_sheet_by_prefix
        save_func = save_section_to_sheet_by_prefix

    flattened_data = flatten_session_state(prefix=section_prefix)
    if not flattened_data:
        st.warning(f"⚠️ No hay datos para guardar en la sección '{section_prefix}'.")
        return

    save_func(id_field=id_field, sheet_name=sheet_name, section_prefix=section_prefix)

# ───────────────────────────────────────────────────────────────────────────────
# 📊 Progreso del formulario
# ───────────────────────────────────────────────────────────────────────────────
def compute_progress(
    session_state: Dict[str, Any],
    section_prefixes: List[str]
) -> Tuple[int, float]:
    if not section_prefixes:
        return 0, 0.0

    completed = sum(
        1 for prefix in section_prefixes if any(
            session_state.get(k) not in (None, "", 0)
            for k in session_state if k.startswith(prefix)
        )
    )

    progress = completed / len(section_prefixes)
    return completed, progress

# ───────────────────────────────────────────────────────────────────────────────
# 🆔 Manejo profesional de autenticación y carga de datos persistentes
# ───────────────────────────────────────────────────────────────────────────────
def validate_ips_id(ips_id: str, lookup_path: str = "data/ips_lookup.json") -> bool:
    """Valida ips_id contra el archivo de lookup."""
    try:
        with open(lookup_path, 'r') as file:
            ips_data = json.load(file)
        return ips_id in ips_data
    except FileNotFoundError:
        st.error("❌ Archivo de lookup no encontrado.")
        return False

def load_persistent_data(ips_id: str) -> None:
    """Carga los datos previos de todas las secciones si existe para la IPS."""
    sections = MINIMUM_HEADERS_BY_SECTION.keys()
    for prefix in sections:
        data = load_existing_data(ips_id=ips_id, sheet_name=prefix.strip("__"))
        if data:
            for key, value in data.items():
                st.session_state[f"{prefix}{key}"] = value

def persist_valid_ips_info(ips_id: str, ips_nombre: str) -> None:
    """Almacena ips_id y nombre de IPS de forma robusta para todas las secciones."""
    st.session_state["ips_id_validado"] = ips_id
    st.session_state["ips_nombre_validado"] = ips_nombre

def get_current_ips_id(session_state=None):
    """Obtiene el identificador único validado de forma persistente."""
    session_state = session_state or st.session_state
    return session_state.get("ips_id_validado", "").strip()

def get_current_ips_nombre(session_state=None):
    """Obtiene el nombre oficial de la IPS validado."""
    session_state = session_state or st.session_state
    return session_state.get("ips_nombre_validado", "").strip()
