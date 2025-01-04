import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
from src._sheets.credentials import init_credentials
import pandas as pd

load_dotenv()

def get_spreadsheet_responses(form_type:str):
    # FORMS NEED TO FOLLOW NAMING CONVENTION
    gc = init_credentials()
    base_name = f"WLDF-{form_type}-Responses"
    print(base_name)

    spreadsheet = gc.open(base_name)
    worksheet = spreadsheet.get_worksheet(0)

    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    print(df.head())

    return df

if __name__ == "__main__":
    get_spreadsheet_responses("Solo")

