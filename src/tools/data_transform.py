import re
import json


class FindDict(object):
    def __init__(self, data: str):
        self.__dicts_list = [
            self.__str_to_dict(str_dict) for str_dict in self.__find_dict(data)
            ]

    def __call__(self):
        return self.__dicts_list

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance()

    def __find_dict(self, data: str) -> list:
        pattern = r'\{"original":.*?\}\]\}'
        dict_list = re.findall(pattern, data)
        return dict_list

    def __str_to_dict(self, str_dict: str) -> dict:
        return json.loads(str_dict)
