import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd

# Google Sheets API Setup
def connect_to_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gspread"], scope)
    client = gspread.authorize(creds)
    sheet = client.open(st.secrets["sheet"]["name"]).sheet1
    return sheet

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

