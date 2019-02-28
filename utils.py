import os

def get_environment_variable(variable_name: str, default_value = None) -> str:
    if variable_name in os.environ:
        return os.environ[variable_name]
    else:
        if default_value != None:
            return default_value
        else:
            raise Exception('The environment variable ' + variable_name + ' is required.')
            