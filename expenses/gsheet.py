"""
Google Sheets API Documentation: https://developers.google.com/sheets/api/quickstart/python
"""

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json
import time
from dotenv import find_dotenv

import environment_variables as env
import notion as notion

start_time = time.time()

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of the google spreadsheet
GOOGLE_SPREADSHEET_ID = env.GOOGLE_SPREADSHEET_ID
RANGE_NAME = "Raw data categorias!A1"

def add_headers_to_array(path, _list: list, db_name: str):
	'''
		Fill in the array given as "_list" with the values located in the given "path"
	'''

	with open(path, 'r') as file:
		data = json.load(file)
		for header in data.get('headers', []):
			if db_name in header:
				_list.extend(header[db_name])
	return _list

def extract_specific_notion_data():
	data = notion.get_notion_data()
	headers = list()
	values = list()
	
	# Appends the headers from the json file to an array if the file exists
	headers_file_name = 'headers.json'
	if os.path.exists(headers_file_name):
		headers_json_path = find_dotenv(filename=headers_file_name)
		add_headers_to_array(headers_json_path, headers, 'categorias')
	else:
		# Creates the json file with the initial structure
		with open(headers_file_name, 'w') as file:
			initial_content = {
				'headers': [
					{
						'categorias': ['ID', 'NAME', 'MES ACTUAL', 'MES ANTERIOR', 'PRESUPUESTO', 'LAST_UPDATED_TIME']
					},
					{
						'gastos': [] # ['ID', 'NAME', 'MES ACTUAL', 'MES ANTERIOR', 'PRESUPUESTO', 'LAST_UPDATED_TIME']
					}
				]
			}
			json.dump(initial_content, file)

	for item in data['results']:
		id = str(notion.safe_get(item, 'properties.ID.unique_id.number'))
		name = str(notion.safe_get(item, 'properties.Name.title.0.plain_text'))
		mes_actual = str(notion.safe_get(item, 'properties.$ Mes actual.formula.number'))
		mes_anterior = str(notion.safe_get(item, 'properties.$ Mes anterior.formula.number'))
		presupuesto = str(notion.safe_get(item, 'properties.Presupuesto.number'))
		
		values.append([id, name, mes_actual, mes_anterior, presupuesto, time.asctime(time.localtime())])
		
	values.sort(key=lambda x : int(x[0]))
	values.insert(0, headers)
	return values


def main():
	creds = None
    # Check if token file exists
	if os.path.exists("token.json"):
		try:
            # Attempt to load credentials from the file
			creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            # If refresh is needed, try to refresh token
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
		except (ValueError, HttpError) as err:
			print(f"Error loading credentials: {err}")
			creds = None  # Reset creds to trigger authorization flow

    # If no valid credentials found, start authorization flow
	if not creds or not creds.valid:
		flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        
		with open("credentials.json", "r") as f:
			google_data = json.load(f)
        
		redirect_uri = google_data["web"]["redirect_uris"][0]
		port = redirect_uri.split(":")[-1].rstrip("/")
		creds = flow.run_local_server(port=int(port))
		# Save the credentials for the next run
		with open("token.json", "w") as token:
			token.write(creds.to_json())

	try:
		service = build("sheets", "v4", credentials=creds)

		# Call the Sheets API
		# valueData = [['Pickles'],['Chocolate'],['Chips'], ['Cookies']]
		valueData = extract_specific_notion_data()
		sheet = service.spreadsheets()
		result = (
			sheet.values()
			.update(spreadsheetId=GOOGLE_SPREADSHEET_ID, range=RANGE_NAME, valueInputOption="USER_ENTERED", body={"values": valueData})
			.execute()
		)
	except HttpError as err:
		print(err)
	

if __name__ == "__main__":
	main()
	
	# Prints a log on the console to meassure the execution time
	print(f'Execution time: {(time.time() - start_time):.2f}s')