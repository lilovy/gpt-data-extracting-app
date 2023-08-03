from dotenv import load_dotenv, find_dotenv
from os import getenv
from src.tools.proxy import proxy_from_file
from src.tools.data_loader import load_token, load_proxy

load_dotenv(find_dotenv())


token1 = getenv('token1')
token2 = getenv('token2')
token3 = getenv('token3')
api_token1 = getenv('api_token1')
api_token2 = getenv('api_token2')

tokens = [
    token1,
    token2,
    token3,
]

token_file = r"resources\chatgpt_tokens\tokens.txt"
tokens = load_token(token_file)

api_tokens = [
    api_token1,
    api_token2,
]

proxy_file = r"resources\proxies\proxy.txt"
proxies = load_proxy(proxy_file)

token_proxy = list(zip(tokens, proxies))

api_prx = list(zip(api_tokens, proxies))

base_proxy_dir = r"resources/proxies/credential/"