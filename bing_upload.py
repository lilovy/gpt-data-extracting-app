from src.database.init_database import DB
from src.tools.data_loader import load_ua
from random import choice


def load(file):
    with open(file, 'r') as f:
        data = f.read().split('\n')
        res = []
        for d in data:
            if len(d) != 0:
                dd = {}
                d_split = d.split(':')
                dd["email"] = d_split[0]
                dd["password"] = d_split[1]
                dd["second_email"] = d_split[2]
                dd["second_password"] = d_split[3]
                res.append(dd)
        # data = [(d.split(':')) for d in data if len(d) != 0]
        return res

def upload(email: str, password: str, second_email: str = None, second_password: str = None, ua: str = None):
    DB.add_bind_session(email, password, second_email, second_password, user_agent=ua)


if __name__ == "__main__":
    ua_file = r"resources\user-agents\bing_user_agents.json"
    for d_args in load("resources\mails/bing_mail.txt"):
        upload(**d_args, ua=choice(load_ua(ua_file)))
