from notion_client import Client
import json
import environment_variables as env

def write_dict_to_file_as_json(content, file_name, extension:str='.json'):
    '''
        Creates a json file with the given content, named as the file_name's value
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

def get_notion_data():
    '''
        1) Authenticates the access to my Notion database through an API Integration
        2) Gets the data from the Notion database
        3) Returns it
    '''
    # Authentication
    client = Client(auth=env.NOTION_SECRET_API_KEY)

    # GET database information (no row's data)
    # db_info = client.databases.retrieve(database_id=env.NOTION_DATABASE_ID_CATEGORIAS)
    # write_dict_to_file_as_json(db_info, 'db_info.json')

    # GET database row's data
    db_rows = client.databases.query(database_id=env.NOTION_DATABASE_ID_CATEGORIAS)
    # write_dict_to_file_as_json(db_rows, 'db_rows.json')

    return db_rows