from multiprocessing import Pool
import time


class Calculate:

    def generator(self):
        i = 0
        while True:
            yield i
            i += 1

    def f(self, x):
        time.sleep(5)
        print(x*x)
        # return x * x

    def run(self):
        p = Pool(2)
        r = p.imap(self.f, self.generator())
        return r


if __name__ == "__main__":
    cl = Calculate()
    r = cl.run()
    for x in r:
        pass
    # print(cl.run())