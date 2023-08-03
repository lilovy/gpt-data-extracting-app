import openai
from random import sample, choice
from time import sleep
import asyncio
import chardet
import json
import re
import unicodedata

from config import proxy_file,base_proxy_dir
from .prompt_loader import LoadPrompt
from .proxy import get_proxy, proxy_from_file
from .data_transform import FindDict
from ..V1.markupGPT import MarkupGPT
from ..V1.edgeGPT import BingGPT
from .tokenizer import num_tokens_from_string as token_sum
from .get_cookie import get_cookie
from .cookie_extract import CookieExtractor
from .data_loader import load_ua
from ..database.init_database import DB
from ..database.DBHelper import BingData, ResultData
from .timer import timer
from .proxynator import Proxynator


class GPTResponser(object):
    def __init__(
        self, 
        token: str,
        prompt: str | list[dict] = None,
        proxy: str = None, 
        ) -> None:

        if prompt:
            self.prompt = prompt
        else:
            self.prompt = ""

        self.__proxy = proxy
        self.__token = token

    def ask(self, question: str | list[dict]):

        if isinstance(question, str):
            question = self.prompt + question
            return self.__unofficial_request(question)

        if isinstance(question, list):
            # if self.prompt != "":
                # question = self.prompt + question
            return self.__official_request(question)

    @property
    def prompt(self) -> str:
        return self.__prompt

    @prompt.setter
    def prompt(self, prompt: str) -> None:
        self.__prompt = prompt

    @timer
    def __official_request(self, message: list[dict]):
        openai.api_key = self.__token
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message,
            temperature=0,
        )
        reply = resp['choices'][0]['message']['content']
        return reply

    def __unofficial_request(self, question: str):

        resp = MarkupGPT(
            access_token=self.__token,
            proxy=self.__proxy,
            )
        return resp.ask(question)


def get_ids_texts(data: list[tuple]):
    ids = []
    texts = []
    for id, text in data:
        ids.append(id)
        texts.append(text)
    return ids, texts

def combine(token, proxy):
    n = 10
    ns = 10000
    prompt = LoadPrompt('prompts/prompt_extract_data.txt').to_str
    proxy = 'http://' + proxy
    num = n
    data = sample(DB.get_raw_data(ns), num)

    while len(data) > 0:
        ids, texts = get_ids_texts(data)

        str_data = str(texts)
        while token_sum(str_data) > 200:
            num -= 1
            data = sample(DB.get_raw_data(ns), num)
            ids, texts = get_ids_texts(data)
            str_data = str(texts)

        print(len(texts), proxy)

        try:
            resp = GPTResponser(token, prompt=prompt, proxy=proxy).ask(str_data)

            if "\\xa0" in resp:
                print('xa0 detect')
                resp = resp.replace("\\xa0", "\u00A0")

            dicts = FindDict(resp)
            if len(dicts) == num:
                result = list(zip(ids, dicts))
                try:
                    DB.insert_result_data(result, ResultData)
                    print("Data successfully uploaded")
                except Exception as e:
                    print(e)
            elif len(dicts) != num:
                print('info is lost')
            # else:
            # print(resp)

        except Exception as e:
            # print(resp)
            if "code: 429" in str(e) or "code: 524" in str(e):
                print(e, f"Token: <{token}>", sep=" <----> ")
                print("Sleep")
                sleep(600)
            # elif "Expecting" in str(e):
            #     print(resp)
            elif "code: 500" in str(e):
                print(e)
                sleep(300)
            else:
                print(e)

        data = sample(DB.get_raw_data(ns), num)
        num = n


def msg(prompt):
    return [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "['Знание adaptive, responsive верстки']"},
        {"role": "assistant", "content": """{"original": "Знание adaptive, responsive верстки", "simple_forms": [{"simple_form": "знание adaptive верстки", "tag": "knowledge"}, {"simple_form": "знание responsive верстки", "tag": "knowledge"}]}"""},
        {"role": "user", "content": "['файер-вол, домен', 'Проектные и мультимодальные перевозки;']"},
        {"role": "assistant", "content": """{"original": "файер-вол, домен", "simple_forms": [{"simple_form": "файер-вол", "tag": "unknown"}, {"simple_form": "домен", "tag": "unknown"}]}, {"original": "Проектные и мультимодальные перевозки;", "simple_forms": [{"simple_form": "проектные перевозки", "tag": "skill"}, {"simple_form": "мультимодальные перевозки", "tag": "skill"}]}"""},
        ]

def api_combine(token, proxy):
    n = 20
    ns = 5000
    prmt = LoadPrompt('prompts\prompt_light_v2.txt').to_str
    proxy = 'http://' + proxy
    num = n
    data = sample(DB.get_raw_data(ns), num)

    while len(data) > 0:
        prompt = prmt
        message = msg(prompt)
        ids, texts = get_ids_texts(data)

        str_data = str(texts)
        # while token_sum(str_data) > 200:
        #     num -= 1
        #     data = sample(DB.get_raw_data(ns), num)
        #     ids, texts = get_ids_texts(data)
        #     str_data = str(texts)
        message += [{"role": "user", "content": str_data}]
        print(len(texts), proxy)

        try:
            resp = GPTResponser(token, proxy=proxy).ask(message)

            dicts = FindDict(resp)
            if len(dicts) != num:
                print('info is lost')
            else:
                result = list(zip(ids, dicts))
                DB.insert_result_data(result, ResultData)

        except Exception as e:
            print(e)
            sleep(30)
            pass

        data = sample(DB.get_raw_data(ns), num)
        num = n

async def bing_combine(cookies: dict, proxy: str):
    n = 10
    ns = 5000
    num = n
    prmt = LoadPrompt('prompts/prompt_extract_data.txt').to_str
    proxy = 'http://' + proxy
    bot = BingGPT(cookies, proxy)
    data = sample(DB.get_raw_data(ns), num)
    # while data

    while len(data) > 0:
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
            # print(response)
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

        except Exception as e:
            if str(e) in ("'messages'", "'text"):
                print(f"Error: {e}")
                sleep(10)
            else:
                print(e)

        data = sample(DB.get_raw_data(ns), num)
        num = n
        sleep(10)
        # break

# async def bing_req(cookies: dict, proxy: str):
    n = 10
    ns = 5000
    num = n
    prmt = LoadPrompt('prompts/prompt_extract_data.txt').to_str
    proxy = 'http://' + proxy
    bot = BingGPT(cookies, proxy)
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

        except Exception as e:
            if str(e) in ("'messages'", "'text"):
                print(f"Error: {e}")
                sleep(600)
            else:
                print(e)

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
                    print(f"Error: {e}")

                    sleep(600)
                else:
                    print(e)
    except Exception as e:
        print(e)


def bing_loop(mail: str, bing: str, login: str):
    while True:
        asyncio.run(bing_req(mail, bing, login))
        sleep(1)

def start_bing(cookies: dict, proxy: str):
    asyncio.run(bing_combine(cookies, proxy))