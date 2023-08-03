from pathlib import Path


class DirMaker(object):
    def __init__(self, f_name: str):
        self.__Path = Path(f_name)

    def make(self):
        if not self.__Path.exists():
            self.__Path.mkdir()

        return self

    def exists(self):
        return self.__Path.exists()
    
    def files(self, pattern: str = "*"):
        files = list(map(lambda x: x.resolve(),self.__Path.glob(pattern))) 
        return files

    @property
    def path(self):
        return self.__Path.resolve()
