from typing import Optional
import streamlit as st
import ast
import json
from utils.google_sheets_client import get_worksheet, get_google_sheet_df
from utils.constants import MINIMUM_HEADERS_BY_SECTION

# ──────────────────────────────────────────────
# Lee el lookup de hash->nombre (ideal: carga solo una vez, por performance)
def load_ips_lookup():
    try:
        with open("data/ips_lookup.json", "r") as f:
            return json.load(f)
    except Exception:
        return {}

# ──────────────────────────────────────────────
# 🔁 Deserializador de valores string → tipo real
def _deserialize_value(value):
    if isinstance(value, str):
        val = value.strip()
        if val.lower() in ["true", "false"]:
            return val.lower() == "true"
        if val.isdigit():
            return int(val)
        try:
            parsed = ast.literal_eval(val)
            if isinstance(parsed, (list, dict)):
                return parsed
        except (ValueError, SyntaxError):
            pass
        if "," in val:
            return [v.strip() for v in val.split(",")]
    return value

# ──────────────────────────────────────────────
# 🧼 Limpieza y normalización del ID de IPS
def _get_cleaned_ips_id(data: dict) -> str:
    return data.get("ips_id", "").strip().lower()

# ──────────────────────────────────────────────
# 📋 Asegura que la hoja tenga todos los encabezados requeridos
def _ensure_headers(sheet, required_keys: list) -> list:
    if not required_keys:
        st.warning("⚠️ No se puede crear hoja sin encabezados válidos.")
        return []
    try:
        current_headers = sheet.row_values(1)
    except Exception:
        current_headers = []
    if not current_headers:
        sheet.resize(rows=1000, cols=len(required_keys))
        sheet.update("A1", [required_keys])
        return required_keys
    missing = [k for k in required_keys if k not in current_headers]
    if missing:
        updated_headers = current_headers + missing
        sheet.resize(rows=sheet.row_count or 1000, cols=len(updated_headers))
        sheet.update("A1", [updated_headers])
        return updated_headers
    return current_headers

# ──────────────────────────────────────────────
# 🔄 Precarga datos existentes para un IPS en una sección (por hoja)
def load_existing_data(ips_id: str, sheet_name: str = "Sheet1") -> Optional[dict]:
    if not ips_id:
        return None
    df = get_google_sheet_df(sheet_name=sheet_name)
    if df.empty or "ips_id" not in df.columns:
        return None
    matched = df[df['ips_id'].str.strip().str.lower() == ips_id.strip().lower()]
    if matched.empty:
        return None
    raw_dict = matched.iloc[0].dropna().to_dict()
    typed_dict = {k: _deserialize_value(v) for k, v in raw_dict.items()}
    return typed_dict

# ──────────────────────────────────────────────
# 🚀 Guarda/actualiza una fila para una sección/hoja (dict plano)
def append_or_update_row(flat_data: dict, sheet_name: str = "Sheet1", ips_nombre: Optional[str] = None) -> bool:
    try:
        sheet = get_worksheet(sheet_name=sheet_name)
        ips_id = _get_cleaned_ips_id(flat_data)
        if not ips_id:
            st.error("❌ El campo `ips_id` es obligatorio para guardar.")
            return False

        # Busca el nombre en lookup si no se pasó explícito
        if not ips_nombre:
            lookup = load_ips_lookup()
            ips_nombre = lookup.get(ips_id, "")

        # Añade el nombre a la fila
        if ips_nombre:
            flat_data["ips_nombre"] = ips_nombre

        # ---- Headers
        expected_headers = list(flat_data.keys())
        headers = _ensure_headers(sheet, expected_headers)
        if not headers:
            st.error(f"❌ No se pudieron establecer encabezados para la hoja '{sheet_name}'.")
            return False

        # Serializa los valores
        def _serialize_value(val):
            if isinstance(val, (dict, list)):
                return str(val)
            if val is None:
                return ""
            return str(val)

        full_row = [_serialize_value(flat_data.get(col, "")) for col in headers]
        existing_rows = sheet.get_all_records()

        for idx, row in enumerate(existing_rows):
            if str(row.get("ips_id", "")).strip().lower() == ips_id:
                sheet.update(f"A{idx + 2}", [full_row])
                return True

        sheet.append_row(full_row, value_input_option="USER_ENTERED")
        return True

    except Exception as e:
        st.error(f"❌ Error al guardar los datos en la hoja '{sheet_name}'.")
        st.exception(e)
        return False

# ──────────────────────────────────────────────
# 💾 Guarda los datos de una sección a partir de un prefijo en session_state
def save_section_to_sheet_by_prefix(id_field: str, sheet_name: str, section_prefix: str, ips_nombre: Optional[str]=None) -> bool:
    if not section_prefix.endswith("__"):
        section_prefix += "__"
    section_data = {
        k[len(section_prefix):]: v
        for k, v in st.session_state.items()
        if k.startswith(section_prefix) and v not in (None, "", [], {})
    }
    # Valida headers mínimos obligatorios (si están definidos)
    required_keys = MINIMUM_HEADERS_BY_SECTION.get(section_prefix, [])
    missing = [
        k for k in required_keys 
        if not str(section_data.get(k, "") if section_data.get(k, "") is not None else "").strip()
    ]
    if missing:
        st.warning(f"⚠️ Faltan campos obligatorios en '{section_prefix}': {', '.join(missing)}")
        return False

    section_data["ips_id"] = id_field.strip()
    # Busca y añade el nombre real
    if not ips_nombre:
        lookup = load_ips_lookup()
        ips_nombre = lookup.get(section_data["ips_id"], "")
    if ips_nombre:
        section_data["ips_nombre"] = ips_nombre
    # Limpia claves basura
    keys_to_remove = [k for k in section_data.keys() if "__" in k]
    for k in keys_to_remove:
        section_data.pop(k)
    return append_or_update_row(section_data, sheet_name=sheet_name, ips_nombre=ips_nombre)

# Alias simple
save_section_to_sheet = save_section_to_sheet_by_prefix

def safe_save_section(id_field: str, sheet_name: str, section_prefix: str, ips_nombre: Optional[str]=None) -> bool:
    try:
        return save_section_to_sheet(id_field, sheet_name, section_prefix, ips_nombre)
    except Exception as e:
        st.warning(f"⚠️ Error inesperado guardando sección '{section_prefix}'.")
        st.exception(e)
        return False

def batch_append_or_update_rows(list_of_dicts, sheet_name, ips_id=None, ips_nombre=None):
    try:
        sheet = get_worksheet(sheet_name=sheet_name)
        if not list_of_dicts:
            st.warning("No hay datos para guardar.")
            return True  # No hay datos, no es un error

        # Determina el nombre si no se pasó
        if ips_id and not ips_nombre:
            lookup = load_ips_lookup()
            ips_nombre = lookup.get(ips_id, "")

        # Asegura que cada dict tenga ips_id y ips_nombre
        for fila in list_of_dicts:
            if ips_id:
                fila["ips_id"] = ips_id
            if ips_nombre:
                fila["ips_nombre"] = ips_nombre

        headers_sheet = sheet.row_values(1)
        headers_dict = list(list_of_dicts[0].keys())
        if not headers_sheet:
            sheet.resize(rows=1000, cols=len(headers_dict))
            sheet.update("A1", [headers_dict])
            headers_sheet = headers_dict
        missing_headers = [h for h in headers_dict if h not in headers_sheet]
        if missing_headers:
            headers_sheet += missing_headers
            sheet.update("A1", [headers_sheet])

        full_rows = []
        for data_dict in list_of_dicts:
            full_rows.append([str(data_dict.get(col, "")) for col in headers_sheet])

        sheet.append_rows(full_rows, value_input_option="USER_ENTERED")
        return True

    except Exception as e:
        st.error(f"❌ Error al guardar datos (batch) en la hoja '{sheet_name}'.")
        st.exception(e)
        return False
