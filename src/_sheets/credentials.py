import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os

load_dotenv()

def init_credentials():
    credentials_file = os.getenv("ACCESS_FILE_NAME")

    SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name(f'{credentials_file}.json', SCOPE)
    gc = gspread.authorize(CREDENTIALS)

    return gc
