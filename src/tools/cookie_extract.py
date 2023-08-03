from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from enum import Enum
from time import sleep
import json

from .mail_reader import get_code
from .errors import BingError
from .data_loader import load_ua


class User:
    def __init__(self, email: str, password: str, second_email: str, second_password: str):
        self.email = email
        self.password = password
        self.second_email = second_email
        self.second_password = second_password

class Conditions(Enum):
    pass

class AuthConditions(Conditions):
    LOGIN_FIELD = "i0116"
    PASSWORD_FIELD = "i0118"
    BLOCK = ""
    ADDITIONAL_EMAIL_FIELD = "iProofEmail"
    # CONFIRM_ADDITIONAL_EMAIL_BUTTON = "iSelectProofAction"
    CODE_VERIFY_V1_FIELD = "iOttText"
    CODE_VERIFY_V2_FIELD = "idTxtBx_OTC_Password"
    # DONT_SHOW_AGAIN_BUTTON = "KmsiCheckboxField"
    NEXT_BUTTON = "idSIButton9"
    # CONFIRM_CODE_BUTTON = "iVerifyCodeAction"
    # UNKNOWN_BUTTON = "id__0"
    PRIVACY_NOTICE_BUTTON = "button.ms-Button.ms-Button--primary"
    STAY_IN_SYSTEM_BUTTON = "button.win-button.button_primary.button.ext-button.primary.ext-primary"



class ChatConditions(Conditions):
    REJECT_COOKIE_BUTTON = "bnp_btn_reject"
    START_CHAT_BUTTON = "codexPrimaryButton"


class States(object):
    LOGIN = "Login"
    PASSWORD = "Password"
    CODE = "Code"
    ADD_LOGIN = "Add-Login"
    BTN = "Btn"
    CSS = "Css"


class ExpectState(object):
    def __init__(self, state, user: User):
        self.state = state
        self.user = user

    def __check(self):
        state = self.state
        user = self.user

        if state == States().LOGIN:
            return user.email

        if state == States().PASSWORD:
            return user.password

        if state == States().ADD_LOGIN:
            return user.second_email

        if state == States().CODE:
            return get_code(
                user.second_email,
                user.second_password,
                delay=5,
            )

        if state == States().CSS:
            return

        if state == States().BTN:
            return

    @property
    def value(self):
        return self.__check()


class CheckCondition(object):
    def __init__(self, condition: Conditions):
        self.__condition = condition

    def __check(self):
        c = self.__condition

        if c == AuthConditions.LOGIN_FIELD:
            return States().LOGIN

        if c == AuthConditions.PASSWORD_FIELD:
            return States().PASSWORD
        
        if c == AuthConditions.ADDITIONAL_EMAIL_FIELD:
            return States().ADD_LOGIN

        if c in (
            AuthConditions.CODE_VERIFY_V1_FIELD,
            AuthConditions.CODE_VERIFY_V2_FIELD,
        ):
            return States().CODE

        else:
            if c in (
                AuthConditions.PRIVACY_NOTICE_BUTTON,
                AuthConditions.STAY_IN_SYSTEM_BUTTON,
            ):
                return States().CSS

            return States().BTN

    @property
    def check(self) -> States:
        return self.__check()


class Element(object):
    def __init__(self, driver: WebDriverWait, log: bool = False):
        self.__driver = driver
        self.log = log

    def get(self, condition: tuple) -> WebElement:
        try:
            element = self.__driver.until(
                EC.visibility_of_element_located(
                    condition,
                )
            )
            return element

        except Exception as e:
            if self.log:
                print(
                    f"({type(self).__name__}): The element  {condition}  was not found"
                )
            pass


class Action(object):
    def __init__(
        self,
        element: WebElement,
        value: str = None,
    ):
        self.element = element
        self.value = value

    def start(self):
        if self.value:
            self.element.send_keys(self.value + Keys.ENTER)
        else:
            self.element.click()


class Driver(object):
    def __init__(self, user_agent: str = None, addon_path: str = None):
        self.__profile = webdriver.FirefoxProfile()
        self.__profile.set_preference(
            "general.useragent.override",
            user_agent,
        )
        self.__driver = webdriver.Firefox(
            firefox_profile=self.__profile,
        )
        if addon_path:
            self.driver.install_addon(addon_path)

    @property
    def driver(self) -> webdriver:
        return self.__driver

    def wait_full_load(self):
        self.driver.execute_script(
            "return document.readyState === 'complete';",
        )

    def get(self, url: str):
        self.__driver.get(url)

    def get_cookie(self):
        cookie = self.__driver.get_cookies()
        self.quite()
        return cookie

    def quite(self):
        self.__driver.quit()


class DriverWait(object):
    def __init__(self, driver: webdriver, timeout: float):
        self.__driver = self.__driver_wait(driver, timeout)
    
    def __driver_wait(self, driver, timeout):
        dr = WebDriverWait(driver, timeout)
        return dr

    @property
    def driver(self):
        return self.__driver


class Routine(object):
    def __init__(self, driver: WebDriverWait, condition: Conditions | tuple, user: User):
        # self.driver = driver
        self.element = Element(driver, log=False)
        self.condition = condition
        self.user = user

    def __get_condition(self):
        state = CheckCondition(self.condition).check
        if state == States().CSS:
            condition = (By.CSS_SELECTOR, self.condition.value)
        else:
            condition = (By.ID, self.condition.value)
        return (state, condition)

    def __get(self, condition: tuple):
        try:
            return self.element.get(condition)
        except Exception as e:
            print(f"{type(self).__name__} -> {Element.__name__}: {e}")

    def __action(self, element: WebElement, value: str):
        try:
            Action(element, value).start()
        except Exception as e:
            print(f"{type(self).__name__} -> {Action.__name__}: {e}")
        return

    def crawl(self):
        state, condition = self.__get_condition()
        element = self.__get(condition)
        value = ExpectState(state, self.user).value

        if element:
            self.__action(element, value)
            return True

    def check(self):
        if self.__get(self.condition):
            return True


class CookieExtractor(object):
    def __init__(
        self, 
        email: str,
        password: str,
        second_email: str,
        second_password: str,
        proxy_path: str = None,
        user_agent: str = None,
        timeout: float = 5,
        addon_path: str = "resources/extensions/foxyproxy_standard-7.5.1.xpi"
    ):
        self.timeout = timeout
        self.user = User(email, password, second_email, second_password)
        self.driver = Driver(user_agent=user_agent, addon_path=addon_path)
        self._driver = self.driver.driver
        self.driver_wait = WebDriverWait(self._driver, timeout)
        self.proxy_path = proxy_path

    def __setup(self):
        driver = self._driver
        dw = self.driver_wait
        driver.switch_to.window(driver.window_handles[-1])

        sleep(1)
        driver.find_element(
            By.CSS_SELECTOR,
            "a[href='/import.html']"
        ).click()

        sleep(1)
        driver.find_element(
            By.CSS_SELECTOR, "input[type='file'][id='importJson']"
        ).send_keys(
            self.proxy_path,
        )

        sleep(1)
        driver.switch_to.alert.accept()

        sleep(1)
        driver.find_element(
            By.CSS_SELECTOR,
            'option[data-i18n="modePatterns"]'
        ).click()

    def __login(self, url: str = "https://login.live.com/"):
        self.driver.get(url)
        for _ in range(2):
            for c in AuthConditions:
                Routine(
                    self.driver_wait,
                    c,
                    self.user,
                    ).crawl()

        # self.driver.get(url)
        condition = (By.CSS_SELECTOR, "a.ms-Link[data-bi-id='sh-sharedshell-home']")
        if Routine(
            WebDriverWait(
                self.driver.driver,
                60,
            ),
            condition,
            self.user,
            ).check():
            print("Authentication complete")
            return True

        print(f"Authentication failed: {self.user.email}")
        return False

    def __session(self, url: str = "https://bing.com/chat"):
        self.driver.get(url)
        for _ in range(2):
            for c in ChatConditions:
                Routine(self.driver_wait, c, self.user).crawl()

        # for _ in range(2):
        #     self.driver.get(url)
        sleep(2)
        return True

    def parse(self):
        self.__setup()
        # print('setup')
        login = self.__login()
        # print('login')
        if login:
            chat = self.__session()
            # print('chat')
            if chat:
                return self.get_cookie
        raise Exception("Login error!")

    @property
    def get_cookie(self):
        return self.driver.get_cookie()


if __name__ == "__main__":
    email = 'mail@outlook.com'
    password = 'pass123'
    second_email = 'mail@ro.ru'
    second_password = 'pass123'
    ua = load_ua('resources/user-agents/bing_user_agents.json')
    CookieExtractor(
        email,
        password,
        second_email,
        second_password,
        user_agent=ua,
        timeout=10,
        ).parse()
