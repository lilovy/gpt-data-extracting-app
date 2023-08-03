import multiprocessing as mp
import threading as tr
from queue import Queue



def multi_process(
    func,
    tokens: list,
    processes: int = 2,
    ):
    print('start parsing!')
    with mp.Pool(processes=processes) as pool:
        pool.map(func, tokens)


def mlt(
    func,
    data,
):
    processes = []
    for t, proxy in data:
        p = mp.Process(target=func, args=(t, proxy,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

def thr(
    func,
    data: list[tuple],
):
    processes = []
    for args in data:
        t = tr.Thread(target=func, args=args)
        processes.append(t)
        t.start()
    # for func, tok_prx in data:
    #     for args in tok_prx:

    for t in processes:
        t.join()

def thr_bing(
    func,
    data: list[dict],
    # data: tuple[object, list[dict]]
):
    processes = []
    # func, data = data
    for d in data:
        mail = d.get('mail')
        bing = d.get('bing')
        login = d.get('login')
        t = tr.Thread(target=func, args=(mail, bing, login))
        processes.append(t)
        t.start()

    for t in processes:
        t.join()

def thr_bing_queue(
    # data: tuple[object, list[dict]],
    func,
    data: list[dict],
    tr_num: int = 2,
):
    queue = Queue()
    # func, data = data
    for d in data:
        queue.put(
            (
                d.get("mail"),
                d.get("bing"),
                d.get("login"),
            )
        )
    
    processes = []
    for _ in range(tr_num):
        # mail = d.get('mail')
        # bing = d.get('bing')
        # login = d.get('login')
        t = tr.Thread(target=func, args=(queue,))
        processes.append(t)
        t.start()

    for t in processes:
        t.join()