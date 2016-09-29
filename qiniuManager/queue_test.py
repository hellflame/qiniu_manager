import os
import time
import Queue
import threading

queue = Queue.Queue(5)
finished = Queue.Queue()
msg_queue = Queue.Queue()


def msg(labors):
    with open("/home/hellflame/total.mdb", 'rb') as handle:
        while True:
            if not queue.full():
                if handle.tell() == os.stat(handle.name).st_size:
                    for i in range(labors):
                        msg_queue.put(1)
                    break
                queue.put(handle.read(4 * 1024 * 1024))
            else:
                print "sleeping"
                time.sleep(1)


def consumer():
    while True:
        if not queue.empty():
            fetch = queue.get()
            finished.put(fetch)
        else:
            if not msg_queue.empty():
                fetch = msg_queue.get()
                if fetch == 1:
                    print 'Done'
                    msg_queue.put(0)
                    break
            else:
                print "lazy"
                time.sleep(1)


def writer(labors):
    tick = 0
    with open("temp", 'wb') as handle:
        while True:
            if not finished.empty():
                get = finished.get()
                handle.write(get)
            else:
                if not msg_queue.empty():
                    fetch = msg_queue.get()
                    if fetch == 0:
                        tick += 1
                        if tick == labors:
                            print "writer Done"
                            break
                else:
                    print "writer free"
                    time.sleep(1)


def run():
    msg_thread = threading.Thread(target=msg, args=(2,))
    msg_thread.start()
    writer_thread = threading.Thread(target=writer, args=(2,))
    labor = []
    for i in range(2):
        labor.append(threading.Thread(target=consumer))
    for i in labor:
        i.start()
    for i in labor:
        i.join()
    writer_thread.start()
    writer_thread.join()
    msg_thread.join()


if __name__ == '__main__':
    run()
