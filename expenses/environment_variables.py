from dotenv import find_dotenv, load_dotenv
import os

dotenv_path = find_dotenv() # Recorre directorios hacia arriba hasta encontrar el archivo .env
load_dotenv(dotenv_path) # Carga el contenido de .env como variables de entorno

NOTION_SECRET_API_KEY = os.getenv("NOTION_SECRET_API_KEY")
NOTION_DATABASE_ID_CATEGORIAS = os.getenv("NOTION_DATABASE_ID_CATEGORIAS")
NOTION_DATABASE_ID_GASTOS = os.getenv("NOTION_DATABASE_ID_GASTOS")
NOTION_DATABASE_ID_INGRESOS = os.getenv("NOTION_DATABASE_ID_INGRESOS")
GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")