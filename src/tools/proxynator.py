from .dir_maker import DirMaker
from .proxy_builder import Schema, ProxyBuilder
from uuid import uuid4


class Proxynator(object):
    def __init__(
        self,
        dirname: str,
        login_proxy: str,
        bing_proxy: str,
        ):
        self.__login = self.__parse(login_proxy)
        self.__bing = self.__parse(bing_proxy)
        self.__dm = DirMaker(dirname)
        self.__dm.make()
        self.__f_dir = fr"{self.dir_path}/{str(uuid4())}.json"


    def __parse(self, proxy: str):
        return {
            x: y
            for x, y in zip(
                ["address", "port", "username", "password"],
                proxy.split(":"),
                )
        }

    @property
    def dir_path(self):
        return self.__dm.path

    @property
    def file_path(self):
        return self.__f_dir

    def create_schema(self):
        file = self.__dm.files()
        if not file:
            schema = ProxyBuilder().build(
                Schema().BING,
                **self.__bing,
                ).build(
                Schema().LOGIN, 
                **self.__login,
                ).export(self.__f_dir)
        else:
            self.__f_dir = str(file[0])
        return self
