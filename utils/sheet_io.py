import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd

# Google Sheets API Setup
def connect_to_sheet():
    """
    Conecta con una hoja de cálculo de Google Sheets utilizando credenciales
    almacenadas en st.secrets y devuelve el objeto Sheet (Worksheet).
    
    Asegura conexión segura y control de errores, recomendado para entorno de producción.
    """
    SPREADSHEET_ID = "1KusiBkYqlL33GmPQN2PfUripYUXVjmDtDG43H-pAmGQ"

    try:
        # Autenticación desde secrets.toml
        client = gspread.service_account_from_dict(st.secrets["gspread"])

        # Abrir hoja por ID directamente (más robusto que por nombre)
        spreadsheet = client.open_by_key(SPREADSHEET_ID)

        # Acceder a la primera hoja (por defecto: Sheet1)
        sheet = spreadsheet.sheet1

        return sheet

    except gspread.exceptions.APIError as api_err:
        st.error("❌ Error de acceso a Google Sheets (APIError). Verifica si habilitaste la API de Google Drive.")
        st.info("Habilita la API en: https://console.developers.google.com/apis/api/drive.googleapis.com/")
        st.exception(api_err)
        st.stop()

    except gspread.exceptions.SpreadsheetNotFound:
        st.error("❌ Hoja de cálculo no encontrada. Verifica si el ID es correcto y si el servicio tiene acceso.")
        st.info(f"ID usado: `{SPREADSHEET_ID}`")
        st.stop()

    except Exception as e:
        st.error("❌ Error inesperado al conectar con Google Sheets.")
        st.exception(e)
        st.stop()

# 🔹 Load data from Google Sheets for a given IPS ID
def load_data_by_ips_id(ips_id):
    sheet = connect_to_sheet()
    records = sheet.get_all_records()
    for row in records:
        if str(row.get("ips_id")).strip().lower() == str(ips_id).strip().lower():
            return row  # Found the IPS data
    return None  # No existing record found

# 🔹 Save data to Google Sheets (append or update)
def append_or_update_row(flat_data: dict):
    sheet = connect_to_sheet()
    ips_id = flat_data.get("identificacion__ips_id")
    if not ips_id:
        st.error("❌ No se ha especificado el ID de la IPS. No se puede guardar.")
        return False

    # Get headers
    headers = sheet.row_values(1)
    records = sheet.get_all_records()

    # Check if IPS exists
    for idx, row in enumerate(records):
        if str(row.get("ips_id")).strip().lower() == str(ips_id).strip().lower():
            # Update the row
            updated_row = [flat_data.get(h, "") for h in headers]
            sheet.update(f"A{idx+2}", [updated_row])
            return True

    # Else: append as new row
    # Ensure new columns are added if new keys found
    new_headers = list(flat_data.keys())
    missing_headers = [h for h in new_headers if h not in headers]

    if missing_headers:
        headers += missing_headers
        sheet.resize(rows=len(records)+2, cols=len(headers))
        sheet.insert_row(headers, index=1)

    # Ensure all headers are respected
    full_row = [flat_data.get(h, "") for h in headers]
    sheet.append_row(full_row, value_input_option="USER_ENTERED")
    return True

