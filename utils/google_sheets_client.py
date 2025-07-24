import gspread
import pandas as pd
import streamlit as st

# 🔑 ID centralizado de Google Sheets desde st.secrets
SPREADSHEET_ID = st.secrets["gcp"]["sheet_id"]

# ──────────────────────────────────────────────
# 1️⃣ Conexión segura a Google Sheets
# ──────────────────────────────────────────────

def get_google_client():
    """
    Obtiene un cliente autenticado de Google Sheets usando las credenciales
    almacenadas en st.secrets["gspread"].
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
    Abre el documento de Google Sheets usando el ID definido en los secretos.
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

# ──────────────────────────────────────────────
# 2️⃣ Obtener o crear hoja automáticamente
# ──────────────────────────────────────────────

def get_worksheet(sheet_name="Sheet1", headers: list[str] = None):
    """
    Obtiene una hoja existente o la crea si no existe.

    Si la hoja es nueva y se proporcionan encabezados, los escribe automáticamente.

    Args:
        sheet_name (str): Nombre de la hoja deseada.
        headers (list[str], opcional): Encabezados para nueva hoja (si aplica).

    Retorna:
        gspread.Worksheet: Objeto de hoja lista para lectura/escritura.
    """
    spreadsheet = get_spreadsheet()

    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        return worksheet
    except gspread.exceptions.WorksheetNotFound:
        if headers is None:
            st.error(f"⚠️ Se intentó crear la hoja `{sheet_name}` pero no se proporcionaron encabezados.")
            st.stop()

        try:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols=str(len(headers)))
            worksheet.append_row(headers)
            return worksheet
        except Exception as e:
            st.error(f"❌ Error al crear la hoja `{sheet_name}`.")
            st.exception(e)
            st.stop()
    except Exception as e:
        st.error(f"❌ Error al acceder a la hoja `{sheet_name}`.")
        st.exception(e)
        st.stop()

# ──────────────────────────────────────────────
# 3️⃣ Descargar datos como DataFrame
# ──────────────────────────────────────────────

def get_google_sheet_df(sheet_name="Sheet1"):
    """
    Descarga los datos actuales de una hoja como DataFrame.

    Args:
        sheet_name (str): Nombre de la hoja a consultar.

    Retorna:
        pd.DataFrame: Datos descargados.
    """
    worksheet = get_worksheet(sheet_name)
    records = worksheet.get_all_records()

    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records)

# ──────────────────────────────────────────────
# 4️⃣ Listar hojas existentes
# ──────────────────────────────────────────────

def list_worksheets():
    """
    Lista los nombres de todas las hojas disponibles.

    Retorna:
        list[str]: Nombres de hojas.
    """
    spreadsheet = get_spreadsheet()
    return [ws.title for ws in spreadsheet.worksheets()]

# ──────────────────────────────────────────────
# 5️⃣ Versión explícita para crear hoja (cuando no es automático)
# ──────────────────────────────────────────────

def get_or_create_worksheet(sheet_name: str, headers: list[str]) -> gspread.Worksheet:
    """
    Similar a `get_worksheet(...)` pero explícita para uso modular.

    Args:
        sheet_name (str): Nombre de la hoja.
        headers (list[str]): Encabezados si se crea nueva hoja.

    Retorna:
        gspread.Worksheet: Hoja lista para escritura.
    """
    return get_worksheet(sheet_name=sheet_name, headers=headers)
