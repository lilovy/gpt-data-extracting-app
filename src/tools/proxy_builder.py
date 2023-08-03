import json


class Schema:
    BING = "bing"
    LOGIN = "login"


class ProxyBuilder(object):

    __schema = {
        "logging": {
            "size": 100,
            "active": False
        },
        "mode": "patterns",
        "bing": {
            "type": 1,
            "color": "#66cc66",
            "title": "bing",
            "active": True,
            "address": "",
            "port": 0,
            "proxyDNS": False,
            "username": "",
            "password": "",
            "whitePatterns": [
                {
                    "title": "all URLs",
                    "pattern": "*",
                    "type": 1,
                    "protocols": 1,
                    "active": False
                },
                {
                    "title": "bing.com",
                    "pattern": "*.bing.com",
                    "type": 1,
                    "protocols": 1,
                    "active": True
                }
            ],
            "blackPatterns": [],
            "pacURL": "",
            "index": 1
        },
        "login": {
            "type": 1,
            "color": "#66cc66",
            "title": "login",
            "active": True,
            "address": "",
            "port": 0,
            "proxyDNS": False,
            "username": "",
            "password": "",
            "whitePatterns": [
                {
                    "title": "all URLs",
                    "pattern": "*",
                    "type": 1,
                    "protocols": 1,
                    "active": False
                },
                {
                    "title": "all URLs",
                    "pattern": "*.live.com",
                    "type": 1,
                    "protocols": 1,
                    "active": True
                },
                {
                    "title": "all URLs",
                    "pattern": "*.microsoft.com",
                    "type": 1,
                    "protocols": 1,
                    "active": True
                }
            ],
            "blackPatterns": [],
            "pacURL": "",
            "index": 0
        },
        "browserVersion": "113.0.1",
        "foxyProxyVersion": "7.5.1",
        "foxyProxyEdition": "standard"
    }

    def __build_schema(self, schema: Schema, address: str, port: int, username: str = "", password: str = ""):
        self.__schema[schema]['address'] = address
        self.__schema[schema]['port'] = port
        self.__schema[schema]['username'] = username
        self.__schema[schema]['password'] = password

        return self

    def build(self, schema: Schema, address: str, port: int, username: str = "", password: str = ""):
        return self.__build_schema(schema, address, port, username, password)
    
    def get(self):
        return json.dumps(self.__schema)

    def export(self, filename: str):
        with open(f'{filename}', 'w') as f:
            json.dump(self.__schema, f, indent=2)
