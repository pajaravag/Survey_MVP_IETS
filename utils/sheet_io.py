import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd

# Google Sheets API Setup
import gspread
import streamlit as st

def connect_to_sheet():
    """
    Establece una conexión segura con Google Sheets usando la cuenta de servicio
    definida en `st.secrets['gspread']`. Devuelve un objeto `Worksheet` conectado
    a la primera hoja ("Sheet1") del archivo identificado por su ID.
    """
    SPREADSHEET_ID = "1KusiBkYqlL33GmPQN2PfUripYUXVjmDtDG43H-pAmGQ"

    try:
        # 1. Autenticación segura desde Streamlit secrets
        client = gspread.service_account_from_dict(st.secrets["gspread"])

        # 2. Acceso al documento por ID (más estable que por nombre)
        spreadsheet = client.open_by_key(SPREADSHEET_ID)

        # 3. Conexión a la primera hoja (Sheet1 por defecto)
        sheet = spreadsheet.sheet1

        return sheet

    except gspread.exceptions.APIError as api_err:
        st.error("❌ Error de autenticación o permisos insuficientes con la API de Google Sheets.")
        st.markdown(
            "- Asegúrate de haber habilitado **Google Sheets API** y **Google Drive API**.\n"
            "- Verifica que el correo del servicio (`client_email`) tenga acceso como *Editor* al archivo.\n"
            "- Espera unos minutos si acabas de habilitar las APIs."
        )
        st.exception(api_err)
        st.stop()

    except gspread.exceptions.SpreadsheetNotFound:
        st.error("❌ Hoja de cálculo no encontrada.")
        st.markdown(f"Verifica que el ID esté correcto: `{SPREADSHEET_ID}`")
        st.info("También asegúrate que el correo de la cuenta de servicio tenga acceso al archivo.")
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

    # Fetch current headers and records
    headers = sheet.row_values(1)
    records = sheet.get_all_records()

    # Ensure headers are unique and updated if new fields appear
    new_keys = list(flat_data.keys())
    missing_headers = [key for key in new_keys if key not in headers]

    if missing_headers:
        headers += missing_headers
        sheet.resize(rows=sheet.row_count, cols=len(headers))
        sheet.update("A1", [headers])  # Only update first row (headers)

    # Prepare full row with aligned headers
    full_row = [flat_data.get(h, "") for h in headers]

    # Check if IPS already exists
    for idx, row in enumerate(records):
        if str(row.get("ips_id")).strip().lower() == str(ips_id).strip().lower():
            sheet.update(f"A{idx + 2}", [full_row])
            return True

    # Append new row
    sheet.append_row(full_row, value_input_option="USER_ENTERED")
    return True


