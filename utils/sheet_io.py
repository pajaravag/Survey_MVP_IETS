import streamlit as st
import pandas as pd
import ast

from utils.google_sheets_client import get_worksheet, get_google_sheet_df
from config import MASTER_CSV  # Ruta local para respaldo

# ──────────────────────────────────────────────
# 🧠 Deserializador de valores string → tipo real
# ──────────────────────────────────────────────
def _deserialize_value(value):
    """
    Convierte un valor string recuperado desde Google Sheets a su tipo original si es posible.

    - Convierte 'True'/'False' a booleano
    - Convierte números enteros
    - Convierte listas serializadas (['a', 'b'])
    - Convierte strings separados por coma a listas
    """
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
# 1️⃣ Cargar datos existentes por IPS
# ──────────────────────────────────────────────
def load_existing_data(ips_id, sheet_name="Sheet1"):
    """
    Carga los datos previamente guardados para una IPS desde Google Sheets
    y los deserializa a sus tipos originales para compatibilidad con Streamlit.
    """
    df = get_google_sheet_df(sheet_name=sheet_name)

    if df.empty or not ips_id:
        return None

    matched = df[df['identificacion__ips_id'].str.strip().str.lower() == ips_id.strip().lower()]
    if matched.empty:
        return None

    raw_dict = matched.iloc[0].dropna().to_dict()

    # Normalizar tipos de datos
    typed_dict = {k: _deserialize_value(v) for k, v in raw_dict.items()}
    return typed_dict

# ──────────────────────────────────────────────
# 2️⃣ Guardar o actualizar fila en Google Sheets y CSV
# ──────────────────────────────────────────────
def append_or_update_row(flat_data: dict, sheet_name="Sheet1"):
    """
    Guarda o actualiza los datos de la encuesta en Google Sheets y respaldo local CSV.
    """
    try:
        sheet = get_worksheet(sheet_name=sheet_name)
        ips_id = flat_data.get("identificacion__ips_id", "").strip().lower()

        if not ips_id:
            st.error("❌ El campo `identificacion__ips_id` es obligatorio para guardar.")
            return False

        headers = sheet.row_values(1)
        existing_rows = sheet.get_all_records()

        # Agregar nuevas columnas si es necesario
        missing_headers = [key for key in flat_data if key not in headers]
        if missing_headers:
            headers += missing_headers
            sheet.resize(rows=sheet.row_count, cols=len(headers))
            sheet.update("A1", [headers])

        # Construir fila ordenada
        full_row = [flat_data.get(col, "") for col in headers]

        # Verificar si ya existe IPS
        for idx, row in enumerate(existing_rows):
            existing_id = str(row.get("identificacion__ips_id", "")).strip().lower()
            if existing_id == ips_id:
                sheet.update(f"A{idx + 2}", [full_row])
                _save_local_backup(flat_data, headers)
                return True

        # Si no existe, agregar nueva fila
        sheet.append_row(full_row, value_input_option="USER_ENTERED")
        _save_local_backup(flat_data, headers)
        return True

    except Exception as e:
        st.error("❌ Error al guardar los datos en Google Sheets.")
        st.exception(e)
        return False

# ──────────────────────────────────────────────
# 3️⃣ Guardar copia local en CSV (respaldo)
# ──────────────────────────────────────────────
def _save_local_backup(flat_data, headers):
    """
    Guarda una copia local en CSV, actualizando si ya existe la IPS.
    """
    try:
        try:
            existing_df = pd.read_csv(MASTER_CSV, dtype=str)
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=headers)

        ips_id = str(flat_data.get("identificacion__ips_id", "")).strip().lower()
        if not ips_id:
            return

        if "identificacion__ips_id" not in existing_df.columns:
            existing_df["identificacion__ips_id"] = ""

        existing_df["identificacion__ips_id"] = (
            existing_df["identificacion__ips_id"]
            .fillna("").astype(str).str.lower()
        )
        match_idx = existing_df[existing_df["identificacion__ips_id"] == ips_id].index

        # Preparar fila nueva como string
        new_row = {col: str(flat_data.get(col, "")) for col in headers}

        prev_nombre = str(existing_df.loc[match_idx[0]].get("identificacion__nombre_responsable", "")).strip() if not match_idx.empty else ""
        nuevo_nombre = str(new_row.get("identificacion__nombre_responsable", "")).strip()

        if prev_nombre and nuevo_nombre and prev_nombre != nuevo_nombre:
            st.warning(f"⚠️ Se detectó un cambio de responsable para esta IPS:\n- Antes: **{prev_nombre}**\n- Ahora: **{nuevo_nombre}**")

        if not match_idx.empty:
            for col in headers:
                existing_df.at[match_idx[0], col] = new_row[col]
        else:
            new_row_df = pd.DataFrame([new_row])
            existing_df = pd.concat([existing_df, new_row_df], ignore_index=True)

        # Asegurar orden y columnas completas
        for col in headers:
            if col not in existing_df.columns:
                existing_df[col] = ""
        existing_df = existing_df[headers]

        existing_df.to_csv(MASTER_CSV, index=False)

    except Exception as e:
        st.warning("⚠️ Error al guardar la copia local en CSV.")
        st.exception(e)
