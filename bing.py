from src.tools.multi import thr_bing, thr_bing_queue
from src.tools.bing_extractor import bing_loop
from src.tools.data_loader import load_cookies
from src.tools.proxy import proxy_from_file
from src.database.init_database import DB
import threading as tr
from queue import Queue


bing_proxy = "resources\proxies\\bing.txt"
login_proxy = "resources\proxies\\login.txt"



if __name__ == "__main__":

    mails = DB.get_emails()

    bing_p = proxy_from_file(bing_proxy)
    login_p = proxy_from_file(login_proxy)

    mail_proxy = [
        {
            "mail": m,
            "bing": b,
            "login": l,
        }
        for m, b, l in list(
            zip(
                mails,
                bing_p,
                login_p,
            )
        )
    ]

    queue = Queue()
    for d in mail_proxy:
        queue.put(d)

    threads = []
    for _ in range(len(bing_p)):
        t = tr.Thread(
            target=bing_loop,
            args=(queue,)
        )
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()




    # thr_bing(bing_loop, data=data)
    # thr_bing_queue(bing_loop, mail_proxy)
