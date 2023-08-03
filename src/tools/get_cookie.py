from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .mail_reader import MailCriteria, EmailReader
from time import sleep


class Browser:
    def __init__(self):
        # firefox_options = webdriver.FirefoxOptions()
        # fire/fox_options.headless = True
        # firefox_options.add_argument('-private')
        self.__firefox_profile = webdriver.FirefoxProfile()    
        self.__firefox_profile.set_preference("general.useragent.override", 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0')
        self.__driver = webdriver.Firefox(firefox_profile=self.__firefox_profile) #options=firefox_options

    def wait_clickable_element(self) -> WebDriverWait:
        self.wait = WebDriverWait(self.__driver, 2)
        return self.wait

    def change_user_agent(self, user_agent: str):
        self.__firefox_profile = webdriver.FirefoxProfile()    
        self.__firefox_profile.set_preference("general.useragent.override", user_agent)
                                              
    def sending_link(self, url: str='https://login.live.com/'):
        self.__driver.get(url=url)
    
    def get_cookies_from_bing(self):
        cookies = self.__driver.get_cookies()
        return cookies
    
    def close_driver(self):
        self.__driver.quit()


class User:
    def __init__(self, email: str, password: str, second_email: str, second_password: str):
        self.email = email
        self.password = password
        self.second_email = second_email
        self.second_password = second_password


class ElementText:    
    def __init__(self, element: str, text: str, wait: WebDriverWait, is_xpath: bool = False):
        self.element = element
        self.__text = text
        self.__is_xpath = is_xpath
        self.__wait = wait

    def action_element(self, email: User):
        try:        
            if self.__is_xpath:
                self.__input_field = self.__wait.until(EC.element_to_be_clickable((By.XPATH, self.element)))
            else:
                self.__input_field = self.__wait.until(EC.element_to_be_clickable((By.ID, self.element)))
            if self.element == 'iOttText' or self.element == 'idTxtBx_OTC_Password':
                sleep(10)
                code = get_code_from_rambler(email)
                print(code)
                self.__input_field.send_keys(code)
            else:
                self.__input_field.send_keys(self.__text)
        except:
            print(f'Пропущен элемент: {self.element}')
            return


class ElementBtn: 
    def __init__(self, element: str, wait: WebDriverWait, is_xpath: bool = False):
        self.element = element
        self.__is_xpath = is_xpath
        self.__wait = wait
 
    def action_element(self, email: User):
        try:
            if self.__is_xpath:
                self.__btn = self.__wait.until(EC.element_to_be_clickable((By.XPATH, self.element)))
            else:
                self.__btn = self.__wait.until(EC.element_to_be_clickable((By.ID, self.element)))
            self.__btn.click()
        except:
            print(f'Пропущен элемент: {self.element}')
            return

    def is_check_btn(self):
        try:
            if self.__wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div/div/a'))):
                return True
        except:
            return False
        

def get_code_from_rambler(email: User):
    with EmailReader(
        client="imap.rambler.ru", 
        email_address=email.second_email, 
        password=email.second_password,
        ) as reader:

        body = reader.get_code_from_email(
            sender_email="account-security-noreply@accountprotection.microsoft.com",
            criteria=MailCriteria.UNSEEN
            )
        if body:
            return body
        else:
            return get_code_from_rambler(email.second_email, email.second_password)    


def get_dict_id_elements(email: User):
    dict_id_elements = {
        'i0116' : ['txt', email.email, False],
        '1idSIButton9' : ['btn', False],
        'i0118' : ['txt', email.password, False],
        '2idSIButton9' : ['btn', False],
        'iProofEmail' : ['txt', email.second_email, False],
        'iSelectProofAction' : ['btn', False],
        'iOttText' : ['txt', 'code', False],
        'iVerifyCodeAction' : ['btn', False],
        '1id__0' : ['btn', False],
        '2id__0' : ['btn', False],
        '1idBtn_Back' : ['btn', False],
        'idTxtBx_OTC_Password' : ['txt', 'code', False],
        '3idSIButton9' : ['btn', False],
        '2idBtn_Back' : ['btn', False],
        'bnp_btn_reject' : ['btn', False],
        '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div/div[3]/div/div[2]/a[1]' : ['btn', True],
        '/html/body/div[1]/div/div[2]/div[2]/div[2]/div/div/div[3]/div/div[2]/a[1]' : ['btn', True],
        }   
    return dict_id_elements


def create_list_object_element(dict_marked_elements: dict, wait: WebDriverWait) -> list[object]:
    list_element_object = []
    for element in dict_marked_elements:
        if dict_marked_elements[element][0] == 'btn':
            if element.find('idSIButton9') != -1 or element.find('idBtn_Back') != -1 or element.find('id__0') != -1:
                 el_btn = ElementBtn(element[1:], wait, dict_marked_elements[element][1])
            else:
                el_btn = ElementBtn(element, wait, dict_marked_elements[element][1])
            list_element_object.append(el_btn)

        elif dict_marked_elements[element][0] == 'txt':
            el_txt = ElementText(element, dict_marked_elements[element][1], wait, dict_marked_elements[element][2])
            list_element_object.append(el_txt)
    return list_element_object

def parser_bing(browser: Browser, email: User, list_objects: list[object]):
        id_element = 0
        for i in range(2):
            for object_el in range(id_element, len(list_objects)):
                if isinstance(list_objects[object_el], ElementBtn):
                    if list_objects[object_el].is_check_btn():
                        browser.sending_link('https://bing.com/chat')
                list_objects[object_el].action_element(email) 
                if i == 1:
                    id_element = 8  
        sleep(3)
        cookie = browser.get_cookies_from_bing()
        # browser.close_driver()
        return cookie

def get_cookie(email: str, password: str, second_email: str, second_password: str):
    user = User(email, password, second_email, second_password)
    browser = Browser()
    browser.sending_link()
    dict_elements = get_dict_id_elements(user)
    wait = browser.wait_clickable_element()
    list_objects = create_list_object_element(dict_elements, wait)
    cookie = parser_bing(browser, user, list_objects)
    return cookie
      

if __name__ == '__main__':
    user = 'mail@outlook.com'
    password = 'pass123'
    second_email = 'mail@ro.ru'
    second_password = 'pass123'
    cookie = get_cookie(user, password, second_email, second_password)
    print(cookie)



