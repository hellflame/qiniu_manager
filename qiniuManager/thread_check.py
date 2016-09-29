import threading
import progress
import Queue
import time


class Check:
    def __init__(self):
        self.queue = Queue.Queue(5)
        self.recorder = Queue.Queue()
        self.progressed = 0
        self.total = 0

    def msg_loop(self):
        index = 10
        out = 0
        while index > 0:
            if not self.queue.full():
                self.queue.put(index)
                index -= 1
            else:
                time.sleep(1)
                out += 1
                if out > 20:
                    break

    def executor(self):
        out = 0
        while True:
            if not self.queue.empty():
                self.queue.get()
                time.sleep(1)
                self.recorder.put(1)
            else:
                out += 1
                if out > 10:
                    break

    @progress.bar()
    def progress_recorder(self):
        self.total = 10
        if not self.recorder.empty():
            self.progressed += self.recorder.get()
        else:
            time.sleep(1)

    def run_loop(self):
        msg_loop = threading.Thread(target=self.msg_loop)
        msg_loop.start()
        ev_loop = []
        progress_thread = threading.Thread(target=self.progress_recorder)
        for i in range(3):
            ev_loop.append(threading.Thread(target=self.executor))
        for i in ev_loop:
            i.start()
        progress_thread.start()
        for i in ev_loop:
            i.join()
        progress_thread.join()
        msg_loop.join()


if __name__ == '__main__':
    Check().run_loop()



