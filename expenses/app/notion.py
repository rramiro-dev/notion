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

    with open(f"{'expenses/json/' + file_name}", 'w') as f:
        f.write(content_as_json_str)

def safe_get(data, dot_chained_keys, default=None):
    '''
        {'a': {'b': [{'c': 1}]}}
        safe_get(data, 'a.b.0.c') -> 1

        Secure way to access to the values within the given argument 'data'
    '''
    keys = dot_chained_keys.split('.')
    for key in keys:
        try:
            if key.isdigit():
                key = int(key)
            data = data[key]
        except (KeyError, IndexError, TypeError):
            return default
    return data

def get_notion_data(_database_id):
    '''
        1) Authenticates the access to my Notion database through an API Integration
        2) Gets the data from the Notion database
        3) Returns it
    '''
    # Authentication
    client = Client(auth=env.NOTION_SECRET_API_KEY)

    # GET database row's data
    db_data = client.databases.query(database_id=_database_id)

    return db_data