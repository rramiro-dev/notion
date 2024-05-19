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

# If modifying these scopes, delete the file token.json
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of the google spreadsheet
GOOGLE_SPREADSHEET_ID = env.GOOGLE_SPREADSHEET_ID
CATEGORIAS_RANGE_NAME = "Raw data categorias!A1"
GASTOS_RANGE_NAME = "Raw data gastos!A1"

def add_headers_to_array(db_name: str):
	'''
		Validates if the headers json file exists, and returns a new list with the headers's data as per the specified "db_name" given argument
	'''
	# If the file exists, it just saves the data as a json object in the 'data' variable. If it doesn't exists, it creates the new json file,
	# and appends the specified data and structure into it
	headers_file_name = 'headers.json'
	if os.path.exists(headers_file_name):
		headers_json_path = find_dotenv(filename=headers_file_name)
		with open(headers_json_path, 'r') as file:
			data = json.load(file)
	else:
		# Creates the json file with the initial structure
		with open(headers_file_name, 'w') as file:
			data = {
				'headers': [
					{
						'categorias': ['ID', 'NAME', 'MES ACTUAL', 'MES ANTERIOR', 'PRESUPUESTO', 'LAST_UPDATED_TIME']
					},
					{
						'gastos': ['ID', 'NAME', 'VALOR', 'FECHA', 'RECURRENTE', 'MEDIO DE PAGO', 'EMPRESA', 'LAST_UPDATED_TIME']
					}
				]
			}
			json.dump(data, file)

	# Iterates over the headers list, and returns them as a new list
	headers = list()
	for header in data.get('headers', []):
		if db_name in header:
			headers.extend(header[db_name])
	return headers

def extract_specific_gastos_notion_data(_database_id):
	aux_categorias = []
	with open('categorias.json', 'r') as file:
		data = json.load(file)
		for categoria in data['results']:
			categoria_long_id = categoria['properties']['id_long']['formula']['string']
			categoria_name = categoria['properties']['Name']['title'][0]['plain_text']
			aux_categorias.append([categoria_long_id, categoria_name])
	
	headers = list()
	values = list()
	data = notion.get_notion_data(_database_id)
	notion.write_dict_to_file_as_json(data, 'gastos')

	for item in data['results']:
		medio_de_pago = str(notion.safe_get(item, 'properties.Medio de pago.select.name'))
		valor = str(notion.safe_get(item, 'properties.Valor.number'))
		empresa = str(notion.safe_get(item, 'properties.Empresa.select.name'))
		fecha = str(notion.safe_get(item, 'properties.Fecha.date.start'))
		recurrente = str(notion.safe_get(item, 'properties.Recurrente?.checkbox'))
		id = str(notion.safe_get(item, 'properties.ID.unique_id.number'))
		name = str(notion.safe_get(item, 'properties.Name.title.0.text.content'))
		categoria_long_id = str(notion.safe_get(item, 'properties.Categor\u00eda.relation.0.id'))
		for item in aux_categorias:
			if item[0] == categoria_long_id:
				categoria = item[1]
				break
			categoria = None
		
		values.append([id, name, valor, fecha, recurrente, medio_de_pago, empresa, time.asctime(time.localtime())])
		
	values.sort(key=lambda x : int(x[0]))
	headers = add_headers_to_array('gastos')
	values.insert(0, headers)
	return values

def extract_specific_categorias_notion_data(_database_id):
	data = notion.get_notion_data(_database_id)
	notion.write_dict_to_file_as_json(data, 'categorias')
	headers = list()
	values = list()
	
	for item in data['results']:
		id = str(notion.safe_get(item, 'properties.ID.unique_id.number'))
		name = str(notion.safe_get(item, 'properties.Name.title.0.plain_text'))
		mes_actual = str(notion.safe_get(item, 'properties.$ Mes actual.formula.number'))
		mes_anterior = str(notion.safe_get(item, 'properties.$ Mes anterior.formula.number'))
		presupuesto = str(notion.safe_get(item, 'properties.Presupuesto.number'))
		
		values.append([id, name, mes_actual, mes_anterior, presupuesto, time.asctime(time.localtime())])
		
	values.sort(key=lambda x : int(x[0]))
	headers = add_headers_to_array('categorias')
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
		# categorias_value_data = [['Pickles'],['Chocolate'],['Chips'], ['Cookies']]
		categorias_value_data = extract_specific_categorias_notion_data(env.NOTION_DATABASE_ID_CATEGORIAS)
		gastos_value_data = extract_specific_gastos_notion_data(env.NOTION_DATABASE_ID_GASTOS)
		sheet = service.spreadsheets()
		categorias_result = (
			sheet.values()
			.update(spreadsheetId=GOOGLE_SPREADSHEET_ID, range=CATEGORIAS_RANGE_NAME, valueInputOption="USER_ENTERED", body={"values": categorias_value_data})
			.execute()
		)
		gastos_result = (
			sheet.values()
			.update(spreadsheetId=GOOGLE_SPREADSHEET_ID, range=GASTOS_RANGE_NAME, valueInputOption="USER_ENTERED", body={"values": gastos_value_data})
			.execute()
		)
	except HttpError as err:
		print(err)

if __name__ == "__main__":
	main()
	
	# Prints a log on the console to meassure the execution time
	print(f'Execution time: {(time.time() - start_time):.2f}s')