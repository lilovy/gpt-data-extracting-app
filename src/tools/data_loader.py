import pickle
import json
# from src.tools import timer
# from .timer import timer
import pandas as pd
from pandas import DataFrame

# @timer
def load_pkl(file):
    with open(file, 'rb') as f:
        data = pickle.load(f)
    return data

# @timer
def load_pandas_pkl(file) -> DataFrame:
    df = pd.read_pickle(file)
    return df

def pickling(data, file, mode = 'ab+'):
    with open(file, mode) as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_cookies(file) -> list[dict]:
    with open(file, 'r') as f:
        cookies = json.load(f)
    return cookies

def load_ua(file) -> list:
    with open(file) as f:
        return json.load(f)

def load_token(filepath: str):
    with open(filepath) as f:
        return [line.replace('\n', '') for line in f.readlines() if len(line) > 1]

def load_proxy(filepath: str) -> str:
    with open(filepath) as f:
        return [line.strip().replace('\n', '') for line in f.readlines() if len(line) > 0]
    #     proxies = f.read().split('\n')
    # return proxies

if __name__ == "__main__":
    # data = load_pkl('.localdata/data_500k.pkl')
    # print(load_proxy(r'resources\proxies\proxy.txt'))
    print(load_token(r"resources\chatgpt_tokens\tokens.txt"))
    # print(data[220100:220310])
    # print(len(data))
    # print(data.head(50))
