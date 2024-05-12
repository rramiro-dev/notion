from notion_client import Client
import json
import environment_variables as env
from time import asctime, localtime

def write_dict_to_file_as_json(content, file_name, extension='.json'):
    '''
        creates a json file with the given content, named as the file_name's value
    '''
    content_as_json_str = json.dumps(content)

    if not file_name.endswith(extension):
        file_name += extension

    with open(file_name, 'w') as f:
        f.write(content_as_json_str)

def safe_get(data, dot_chained_keys):
    '''
        {'a': {'b': [{'c': 1}]}}
        safe_get(data, 'a.b.0.c') -> 1

        Secure way to access to the values within the given argument 'data'
    '''
    keys = dot_chained_keys.split('.')
    for key in keys:
        try:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data[key]
        except (KeyError, TypeError, IndexError):
            return None
    return data

def main():
    # Authentication
    client = Client(auth=env.NOTION_SECRET_API_KEY)

    # Creates a database json file
    db_info = client.databases.retrieve(database_id=env.NOTION_DATABASE_ID_CATEGORIAS)
    write_dict_to_file_as_json(db_info, 'db_info.json')

    # Creates a database's rows json file
    db_rows = client.databases.query(database_id=env.NOTION_DATABASE_ID_CATEGORIAS)
    write_dict_to_file_as_json(db_rows, 'db_rows.json')

    # Access to database's rows data``
    simplified_rows = []

    for row in db_rows['results']:
        id = safe_get(row, 'properties.ID.unique_id.number')
        name = safe_get(row, 'properties.Name.title.0.plain_text')
        mes_actual = safe_get(row, 'properties.$ Mes actual.formula.number')
        mes_anterior = safe_get(row, 'properties.$ Mes anterior.formula.number')
        presupuesto = safe_get(row, 'properties.Presupuesto.number')

        simplified_rows.append({
            'id': id,
            'name': name,
            'mes_actual': mes_actual,
            'mes_anterior': mes_anterior,
            'presupuesto': presupuesto,
            'last_updated_time': asctime(localtime())
        })

    write_dict_to_file_as_json(simplified_rows, 'simplified_rows.json')

if __name__ == '__main__':
    main()