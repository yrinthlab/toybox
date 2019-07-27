# coding: utf-8 

import threading
import multiprocessing
import queue
import traceback

class BackgroundBuffer:
    """
    Data buffer loading data at backgroud
    """

    def __init__(self, data_iter, buf_size, timeout=None, mode='thread'):
        """
        data_iter: iterator of data need to be loaded
        timeout: in seconds
        mode: 'thread' or 'proccess'. 'process' not working on windows currently.
        """
        super().__init__()
        self.data_iter = data_iter
        self._buf = queue.Queue(buf_size)
        self.timeout = timeout

        if mode == 'thread':
            threading.Thread(target=self.run).start()
        elif mode == 'process':
            # not working on Windows
            multiprocessing.Process(target=self.run).start()

    def __call__(self):
        self.run()

    def run(self):
        try:
            for v in self.data_iter:
                self._buf.put((v, None)) #(data, error)
            # raise StopIteration again manually 
            raise StopIteration
        except Exception as e:
            # `get` will hang forever, if there'no item in queue.
            # when there's no more data or some Exception happened, 
            # we `put` a special item in queue to release `get` 
            # and tell it what happend.
            self._buf.put((traceback.format_exc(), e))

    def __next__(self):
        d, e = self._buf.get()
        if e:
            # make sure this object cannot be used again
            self._buf.put((None, StopIteration))
            # if everything goes ok, this's supossed to be StopIteration.
            raise e
        return d

    def __iter__(self):
        return self

if __name__ == '__main__':
    # test
    import time
    def data():
        for i in range(3):
            time.sleep(1)
            yield i

    b = BackgroundBuffer(data(), 2)
    for i in b:
        print(i)
