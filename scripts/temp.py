import time
import threading

class ThreadTest:

    def __init__(self):
        self.i = 0
        self.thread = threading.Thread(target=self.update_i)
        self.running = True
        # self.thread.start()

    def update_i(self):
        while self.running:
            self.i += 1
            print(self.i)
            time.sleep(1)

    def run(self):
        self.thread.start()

    def stop(self):
        self.running = False

    def __del__(self):
        self.running = False


if __name__ == "__main__":
    test = ThreadTest()
    test.run()
    time.sleep(10)
    test.stop()
