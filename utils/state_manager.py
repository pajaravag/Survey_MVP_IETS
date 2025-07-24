import streamlit as st
from datetime import datetime
from typing import Callable, Optional, Tuple, List, Dict, Any
from utils.constants import MINIMUM_HEADERS_BY_SECTION

# ───────────────────────────────────────────────────────────────────────────────
# 🔧 Aplanar el estado de sesión en un diccionario plano por prefijo
# ───────────────────────────────────────────────────────────────────────────────

def flatten_session_state(
    session_state: Optional[Dict[str, Any]] = None,
    prefix: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extrae claves que comienzan con un prefijo y devuelve un dict plano
    con las claves sin prefijo, solo si el valor es escalar (str/int/float/bool/None).

    Args:
        session_state (dict, optional): Estado de sesión a usar. Si no se proporciona,
            se usa `st.session_state`.
        prefix (str, optional): Prefijo con '__' al final. Si no se proporciona, retorna todo
            el estado de sesión.

    Returns:
        dict: Diccionario plano sin el prefijo en las claves.
    """
    session_state = session_state or st.session_state

    def is_scalar(val):
        return isinstance(val, (str, int, float, bool)) or val is None

    if prefix:
        if not prefix.endswith("__"):
            prefix += "__"
        # NO incluyas claves iguales al prefix (ej: "identificacion__")
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
    """
    Registra la marca de tiempo y guarda la sección en una hoja de cálculo.

    Args:
        section_prefix (str): Prefijo que identifica los campos de la sección.
        id_field (str): ID único del IPS o institución.
        sheet_name (str): Nombre de la hoja de destino.
        save_func (callable, optional): Función de guardado con firma
            (section_prefix, id_field, sheet_name). Si no se especifica, usa la predeterminada.
    """
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


def get_current_ips_id(session_state):
    """
    Busca el identificador único de la IPS a lo largo de las posibles claves.
    """
    return (
        session_state.get("identificacion__ips_id")
        or session_state.get("intro__id_ips")
        or session_state.get("identificacion", {}).get("ips_id")
        or ""
    ).strip()