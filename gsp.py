from google.oauth2.service_account import Credentials
import gspread
import streamlit as st

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)

gc = gspread.authorize(credentials)

def get_cell(url: str, work_sheet: gspread.worksheet.Worksheet, cell_name: str) -> (str | None):
    try:
        sheet = gc.open_by_url(url)
        ws = sheet.worksheet(work_sheet)
        cell = ws.acell(cell_name)
        return cell.value
    except Exception as e:
        print(e)
        return None

def get_range(url: str, work_sheet: gspread.worksheet.Worksheet, cell_range: str) -> (list[str] | None):
    try:
        sheet = gc.open_by_url(url)
        ws = sheet.worksheet(work_sheet)
        cell = ws.range(cell_range)
        return [c.value for c in cell]
    except Exception as e:
        print(e)
        return None
