import json
from modules.consolelog import log


class JsonHandler:
    def __init__(self, path):
        try:
            self.__filePath = path
            self.__file = open(path, "r").read()
        except Exception as e:
            log("JSON", 1, e)
        else:
            self.__json = json.loads(self.__file)
            log("JSON", 0, "Loaded {}".format(self.__filePath))

    def toString(self):
        return json.dumps(self.__json)

    def json(self):
        return self.__json

    def value(self, key):
        return self.__json[key]

    def setValue(self, key, value):
        try:
            self.__json[key] = value
        except Exception as e:
            log("JSON", 1, e)
            return False
        else:
            return True
