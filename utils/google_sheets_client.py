import gspread
import pandas as pd
import streamlit as st

# 🔑 Google Sheets Document ID (centralized here for reuse)
SPREADSHEET_ID = "1KusiBkYqlL33GmPQN2PfUripYUXVjmDtDG43H-pAmGQ"

# 🔹 1. Connect to Google Sheets
def connect_to_sheet():
    """
    Establece una conexión segura con Google Sheets usando las credenciales
    de servicio guardadas en `st.secrets['gspread']`.

    Devuelve:
        Worksheet: Hoja activa (Sheet1) conectada.
    """
    try:
        client = gspread.service_account_from_dict(st.secrets["gspread"])
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.sheet1
        return sheet

    except gspread.exceptions.APIError as api_err:
        st.error("❌ Error de autenticación o permisos con la API de Google Sheets.")
        st.markdown("""
            - Verifique que las APIs de Google Sheets y Drive estén habilitadas.
            - Confirme que el correo de la cuenta de servicio tiene acceso como *Editor* al archivo.
        """)
        st.exception(api_err)
        st.stop()

    except gspread.exceptions.SpreadsheetNotFound:
        st.error("❌ No se encontró el archivo de Google Sheets.")
        st.markdown(f"Verifique el ID del archivo: `{SPREADSHEET_ID}`")
        st.stop()

    except Exception as e:
        st.error("❌ Error inesperado al conectar con Google Sheets.")
        st.exception(e)
        st.stop()


# 🔹 2. Get Google Sheet as pandas DataFrame
def get_google_sheet_df():
    """
    Descarga los datos actuales de Google Sheets como un DataFrame de pandas.

    Retorna:
        pd.DataFrame: Todos los registros de la hoja como DataFrame.
    """
    sheet = connect_to_sheet()
    data = sheet.get_all_records()

    if not data:
        return pd.DataFrame()  # Return empty DataFrame if no records

    df = pd.DataFrame(data)
    return df

