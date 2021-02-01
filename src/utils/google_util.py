import discord
import json
from discord.ext import commands
from google.oauth2 import service_account
from googleapiclient.discovery import build
from utils.color_util import blue, magenta
from pprint import pprint

sheet_id = None
credentials = None
headers = None

def setup():
    global sheet_id
    global credentials
    global headers

    config_file = open('savedata\\config.json','r')
    sheet_id = json.loads(config_file.read())['sheet_id']
    config_file.close()

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'savedata\\creds.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range="Movies!A1:1", majorDimension='COLUMNS').execute()
    headers = []
    header_data = result.get('values', [])

    for value in header_data:
        headers.append(value[0])

    # result = sheet.get(spreadsheetId=self.sheet_id, ranges="Movies!A1:I72").execute()
    # pprint(result['sheets'])

def get_headers():
    global headers
    setup()
    return headers