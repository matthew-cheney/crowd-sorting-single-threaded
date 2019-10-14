import yaml
import os

class yamlReader():
    @staticmethod
    def readConfig(filename, app):
        try:
            filename = os.path.join(os.path.dirname(__file__), '..', filename,)
            with open(filename, "r") as config:
                data_loaded = yaml.safe_load(config)
        except yaml.YAMLError as exc:
            print(exc)
            return
        app.config['APP_ROOT'] = os.path.dirname(os.path.abspath(__file__))
        for key in data_loaded:
            if key == 'APP_DOCS':
                app.config[key] = os.path.join(app.config['APP_ROOT'], data_loaded[key])
            else:
                app.config[key] = data_loaded[key]
                print("read in", key, ";", data_loaded[key])
        # SQLALCHEMY_BINDS from db


    @staticmethod
    def readDatabases(filename, app):
        try:
            filename = os.path.join(os.path.dirname(__file__), '..', filename,)
            with open(filename, "r") as f:
                file_contents = '{' + f.read() + '}'
        except FileNotFoundError as exc:
            print(exc)
            return
        app.config['SQLALCHEMY_BINDS'] = file_contents
