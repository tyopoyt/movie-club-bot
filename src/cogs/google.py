import discord
import json
from discord.ext import commands
from google.oauth2 import service_account
from googleapiclient.discovery import build
from utils.color_util import blue, magenta
from pprint import pprint

def setup(movie_bot):
    movie_bot.add_cog(Google(movie_bot))

class Google(commands.Cog):
    credentials = None
    sheet_id = None

    def __init__(self, movie_bot):
        self.movie_bot = movie_bot

        config_file = open('savedata\\config.json','r')
        self.sheet_id = json.loads(config_file.read())['sheet_id']
        config_file.close()

        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = 'savedata\\creds.json'
        self.credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=self.credentials)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.sheet_id, range="Movies!A1:I72", majorDimension='COLUMNS').execute()
        values = result.get('values', [])
        # pprint(values)

        # result = sheet.get(spreadsheetId=self.sheet_id, ranges="Movies!A1:I72").execute()
        # pprint(result['sheets'])
