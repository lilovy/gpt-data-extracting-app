from random import sample, choice
from time import sleep
import asyncio
import threading
import functools
from queue import Queue, Empty

from config import base_proxy_dir
from .prompt_loader import LoadPrompt
from .errors import DayLimit
from .data_transform import FindDict
from ..V1.edgeGPT import BingGPT
from .cookie_extract import CookieExtractor
from ..database.init_database import DB
from ..database.DBHelper import BingData
from .proxynator import Proxynator


def retry_on_exception(func):
    @functools.wraps(func)
    def wrapper(queue: Queue):
        processed_proxies = set()
        while True:
            try:
                arguments = queue.get(block=False)
                mail = arguments["mail"]
                bing = arguments["bing"]
                login = arguments["login"]
                if bing not in processed_proxies:
                    processed_proxies.add(bing)
                    func(mail=mail, bing=bing, login=login)
                else:
                    print(f"Skipping {mail} with duplicate proxy {bing}")
            except Empty:
                break
            except Exception as e:
                print(f"Exception: {e}. Getting a new args...")
                try:
                    processed_proxies.discard(bing)
                    queue.put(arguments)
                except:
                    pass
    return wrapper


def get_ids_texts(data: list[tuple]):
    ids = []
    texts = []
    for id, text in data:
        ids.append(id)
        texts.append(text)
    return ids, texts


def get_cookies(
    email: str,
    bing_proxy: str,
    login_proxy: str,
    ):
    cookie = DB.get_cookie(email)
    if not cookie:
        p_dir = base_proxy_dir + email
        proxy_path = Proxynator(
            p_dir,
            login_proxy, 
            bing_proxy,
            ).create_schema().file_path
        auth_data = DB.get_auth_data(email)
        cookie = CookieExtractor(
            **auth_data,
            timeout=2,
            proxy_path=proxy_path,
            ).parse()
        # print(cookie)
        DB.update_bing_cookie(email, cookie)
        cookie = DB.get_cookie(email)
    return cookie

async def bing_req(
    email: str,
    bing_proxy: str,
    login_proxy: str,
    ):
    n = 10
    ns = 10000
    num = n
    prmt = LoadPrompt('prompts/prompt_extract_data.txt').to_str

    proxy = 'http://' + bing_proxy
    # cookie = DB.get_cookie(email)

    # if not cookie:
    try:
        cookie = get_cookies(
            email,
            bing_proxy,
            login_proxy,
        )
    except Exception as e:
        print(f"cookie: {e}")

    try:
        bot = BingGPT(cookie, proxy)

        data = sample(DB.get_raw_data(ns), num)

        if len(data) > 0:
            ids, texts = get_ids_texts(data)
            str_data = str(texts)
            prompt = prmt + str_data

            while len(prompt) > 2000:
                num -= 1
                data = sample(DB.get_raw_data(ns), num)
                ids, texts = get_ids_texts(data)
                str_data = str(texts)
                prompt = prmt + str_data
            print(len(prompt), num, proxy)

            try:
                task = asyncio.create_task(bot.ask(prompt))
                response: str = await task
                if "\\xa0" in response:
                    print('xa0 detect')
                    response = response.replace("\\xa0", "\u00A0")
                dicts = FindDict(response)

                if len(dicts) != num:
                    # print(response)
                    print('info is lost')
                else:
                    result = list(zip(ids, dicts))
                    DB.insert_result_data(result, BingData)

            except BaseException as e:
                if str(e) in ("'messages'", "'text'"):
                    # print(f"Error: {e}")

                    # sleep(600)
                    raise DayLimit()
                else:
                    print(e)
    except Exception as e:
        print(e)


@retry_on_exception
def bing_loop(mail: str, bing: str, login: str):
    print(f"Thread: {threading.get_native_id()}")
    while True:
        try:
            asyncio.run(bing_req(mail, bing, login))
            sleep(1)
        except DayLimit as e:
            print(e.message)
            raise

@retry_on_exception
def start_bing(mail: str, bing: str, login: str):
    asyncio.run(bing_req(mail, bing, login))
