import streamlit as st
import pandas as pd
from utils.google_sheets_client import get_worksheet, get_google_sheet_df

from config import MASTER_CSV  # ✅ Para guardar backup local


# ──────────────────────────────────────────────
# 1️⃣ Cargar datos existentes por IPS
# ──────────────────────────────────────────────

def load_existing_data(ips_id, sheet_name="Sheet1"):
    """
    Carga los datos previamente guardados para un IPS específico desde Google Sheets.

    Args:
        ips_id (str): Identificador único de la IPS (case-insensitive).
        sheet_name (str): Nombre de la hoja. Por defecto "Sheet1".

    Retorna:
        dict | None: Diccionario de datos si existe, None si no hay coincidencia.
    """
    df = get_google_sheet_df(sheet_name=sheet_name)

    if df.empty or not ips_id:
        return None

    matched = df[df['identificacion__ips_id'].str.strip().str.lower() == ips_id.strip().lower()]
    if matched.empty:
        return None

    return matched.iloc[0].dropna().to_dict()


# ──────────────────────────────────────────────
# 2️⃣ Guardar o actualizar fila en Google Sheets y CSV
# ──────────────────────────────────────────────

def append_or_update_row(flat_data: dict, sheet_name="Sheet1"):
    """
    Guarda o actualiza los datos de la encuesta en Google Sheets y en archivo CSV local.

    Args:
        flat_data (dict): Diccionario aplanado con todas las claves y valores.
        sheet_name (str): Nombre de la hoja en Google Sheets.

    Retorna:
        bool: True si la operación fue exitosa, False si hubo error.
    """
    try:
        sheet = get_worksheet(sheet_name=sheet_name)
        ips_id = flat_data.get("identificacion__ips_id", "").strip().lower()

        if not ips_id:
            st.error("❌ El campo `identificacion__ips_id` es obligatorio para guardar.")
            return False

        # Obtener encabezados y registros actuales
        headers = sheet.row_values(1)
        existing_rows = sheet.get_all_records()

        # Verificar encabezados adicionales y actualizar si es necesario
        missing_headers = [key for key in flat_data.keys() if key not in headers]
        if missing_headers:
            headers += missing_headers
            sheet.resize(rows=sheet.row_count, cols=len(headers))
            sheet.update("A1", [headers])

        # Preparar la fila completa respetando los encabezados
        full_row = [flat_data.get(col, "") for col in headers]

        # Buscar fila existente por IPS y actualizar si aplica
        for idx, row in enumerate(existing_rows):
            existing_id = str(row.get("identificacion__ips_id", "")).strip().lower()
            if existing_id == ips_id:
                sheet.update(f"A{idx + 2}", [full_row])  # idx + 2 → compensar encabezado
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
# 3️⃣ Guardar copia local en CSV
# ──────────────────────────────────────────────

def _save_local_backup(flat_data, headers):
    """
    Guarda una copia local de los datos en un CSV de respaldo.

    Args:
        flat_data (dict): Datos a guardar.
        headers (list): Lista completa de encabezados.
    """
    try:
        # Leer o crear DataFrame
        try:
            existing_df = pd.read_csv(MASTER_CSV)
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=headers)

        # Verificar si el IPS ya existe localmente
        ips_id = flat_data.get("identificacion__ips_id", "").strip().lower()
        if ips_id:
            existing_df["identificacion__ips_id"] = existing_df["identificacion__ips_id"].fillna("").astype(str).str.lower()
            match_idx = existing_df[existing_df["identificacion__ips_id"] == ips_id].index

            new_row = {col: flat_data.get(col, "") for col in headers}

            if not match_idx.empty:
                existing_df.loc[match_idx[0]] = new_row
            else:
                existing_df = pd.concat([existing_df, pd.DataFrame([new_row])], ignore_index=True)

            existing_df.to_csv(MASTER_CSV, index=False)
    except Exception as e:
        st.warning("⚠️ Error al guardar la copia local en CSV.")
        st.exception(e)
