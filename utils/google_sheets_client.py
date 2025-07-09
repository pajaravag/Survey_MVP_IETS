import gspread
import pandas as pd
import streamlit as st

# 🔑 ID centralizado de Google Sheets (evitar hardcode repetido)
SPREADSHEET_ID = "1KusiBkYqlL33GmPQN2PfUripYUXVjmDtDG43H-pAmGQ"


# ──────────────────────────────────────────────
# 1️⃣ Conexión segura a Google Sheets
# ──────────────────────────────────────────────

def get_google_client():
    """
    Obtiene un cliente autenticado de Google Sheets usando las credenciales de servicio
    almacenadas en `st.secrets`.

    Retorna:
        gspread.Client: Cliente autenticado.
    """
    try:
        client = gspread.service_account_from_dict(st.secrets["gspread"])
        return client
    except Exception as e:
        st.error("❌ Error al autenticar con Google. Verifique las credenciales en st.secrets.")
        st.exception(e)
        st.stop()


def get_spreadsheet():
    """
    Abre el documento de Google Sheets usando el ID centralizado.

    Retorna:
        gspread.Spreadsheet: Objeto Spreadsheet.
    """
    try:
        client = get_google_client()
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        return spreadsheet
    except gspread.exceptions.SpreadsheetNotFound:
        st.error("❌ No se encontró el archivo de Google Sheets.")
        st.markdown(f"🔗 Verifique el ID proporcionado: `{SPREADSHEET_ID}`")
        st.stop()
    except Exception as e:
        st.error("❌ Error al acceder al Google Spreadsheet.")
        st.exception(e)
        st.stop()


def get_worksheet(sheet_name="Sheet1"):
    """
    Obtiene una hoja específica dentro del documento de Google Sheets.

    Args:
        sheet_name (str): Nombre de la hoja. Por defecto "Sheet1".

    Retorna:
        gspread.Worksheet: Objeto Worksheet de la hoja seleccionada.
    """
    try:
        spreadsheet = get_spreadsheet()
        worksheet = spreadsheet.worksheet(sheet_name)
        return worksheet
    except gspread.exceptions.WorksheetNotFound:
        st.error(f"❌ No se encontró la hoja `{sheet_name}` en el archivo de Google Sheets.")
        st.stop()
    except Exception as e:
        st.error("❌ Error al acceder a la hoja dentro del Spreadsheet.")
        st.exception(e)
        st.stop()


# ──────────────────────────────────────────────
# 2️⃣ Descargar datos como DataFrame
# ──────────────────────────────────────────────

def get_google_sheet_df(sheet_name="Sheet1"):
    """
    Descarga los datos actuales de una hoja de Google Sheets como DataFrame.

    Args:
        sheet_name (str): Nombre de la hoja a descargar.

    Retorna:
        pd.DataFrame: Datos de la hoja en DataFrame (vacío si sin registros).
    """
    worksheet = get_worksheet(sheet_name)
    records = worksheet.get_all_records()

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    return df


# ──────────────────────────────────────────────
# 3️⃣ (Opcional) Obtener todas las hojas disponibles
# ──────────────────────────────────────────────

def list_worksheets():
    """
    Lista los nombres de todas las hojas disponibles en el archivo de Google Sheets.

    Retorna:
        list[str]: Lista de nombres de hojas.
    """
    spreadsheet = get_spreadsheet()
    return [ws.title for ws in spreadsheet.worksheets()]
