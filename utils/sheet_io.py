import gspread
import streamlit as st
import pandas as pd
from utils.google_sheets_client import get_google_sheet_df  # Assumed external file

# 🔹 1. Connect to Google Sheets
def connect_to_sheet():
    """
    Establece una conexión segura con Google Sheets usando las credenciales
    definidas en `st.secrets['gspread']`. Retorna un objeto Worksheet.
    """
    SPREADSHEET_ID = "1KusiBkYqlL33GmPQN2PfUripYUXVjmDtDG43H-pAmGQ"

    try:
        client = gspread.service_account_from_dict(st.secrets["gspread"])
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.sheet1
        return sheet

    except gspread.exceptions.APIError as api_err:
        st.error("❌ Error de autenticación o permisos insuficientes con la API de Google Sheets.")
        st.markdown(
            "- Verifica que las APIs de Google Sheets y Google Drive están habilitadas.\n"
            "- Revisa los permisos del correo de la cuenta de servicio."
        )
        st.exception(api_err)
        st.stop()

    except gspread.exceptions.SpreadsheetNotFound:
        st.error("❌ Hoja de cálculo no encontrada.")
        st.markdown(f"Verifica que el ID esté correcto: `{SPREADSHEET_ID}`")
        st.stop()

    except Exception as e:
        st.error("❌ Error inesperado al conectar con Google Sheets.")
        st.exception(e)
        st.stop()

# 🔹 2. Load existing data from Google Sheets for a given IPS ID
def load_existing_data(ips_id):
    """
    Carga los datos previamente guardados para un IPS ID específico desde Google Sheets.

    Parámetros:
        ips_id (str): Identificador único de la IPS.

    Retorna:
        dict o None: Datos en formato diccionario si existe, o None si no hay datos.
    """
    df = get_google_sheet_df()

    if df.empty or not ips_id:
        return None

    # Match exact IPS ID (case-insensitive)
    match = df[df['identificacion__ips_id'].str.strip().str.lower() == ips_id.strip().lower()]
    if match.empty:
        return None

    return match.iloc[0].dropna().to_dict()

# 🔹 3. Save or update a row in Google Sheets based on IPS ID
def append_or_update_row(flat_data: dict):
    """
    Guarda o actualiza los datos de la encuesta en Google Sheets para un IPS específico.

    Parámetros:
        flat_data (dict): Diccionario plano con todos los campos del formulario.

    Retorna:
        bool: True si se guardó correctamente, False si hubo error.
    """
    sheet = connect_to_sheet()
    ips_id = flat_data.get("identificacion__ips_id")

    if not ips_id:
        st.error("❌ No se ha especificado el ID de la IPS. No se puede guardar.")
        return False

    # 1. Obtener encabezados y registros actuales
    headers = sheet.row_values(1)
    records = sheet.get_all_records()

    # 2. Verificar si hay nuevos campos y actualizar encabezados si es necesario
    missing_headers = [key for key in flat_data.keys() if key not in headers]
    if missing_headers:
        headers += missing_headers
        sheet.resize(rows=sheet.row_count, cols=len(headers))
        sheet.update("A1", [headers])

    # 3. Preparar la fila completa alineada con los encabezados
    full_row = [flat_data.get(col, "") for col in headers]

    # 4. Buscar si la IPS ya existe y actualizarla
    for idx, row in enumerate(records):
        existing_id = str(row.get("identificacion__ips_id", "")).strip().lower()
        if existing_id == ips_id.strip().lower():
            sheet.update(f"A{idx + 2}", [full_row])  # idx+2 to account for header row
            return True

    # 5. Si no existe, agregar como nueva fila
    sheet.append_row(full_row, value_input_option="USER_ENTERED")
    return True
