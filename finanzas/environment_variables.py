import os

from dotenv import find_dotenv, load_dotenv

# Recorre directorios hacia arriba hasta encontrar el archivo .env
dotenv_path = find_dotenv()

# Carga el contenido de .env como variables de entorno
load_dotenv(dotenv_path)

API_KEY = os.getenv("API_KEY")
PAGE_ID = os.getenv("PAGE_ID")