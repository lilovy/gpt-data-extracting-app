from src.tools.multi import thr
from src.tools.extractor import combine
from config import token_proxy


if __name__ == "__main__":
    thr(combine, token_proxy)
