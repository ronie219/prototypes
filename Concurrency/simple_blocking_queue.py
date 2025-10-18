import threading


class SimpleBlockingQueue:

    def __init__(self, max_size):
        self.max_size = max_size
        self.items = []
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)

    def put(self, item):
        with self.not_full:
            while 0 < self.max_size <= len(self.items):
                self.not_full.wait()
            self.items.append(item)
            self.not_empty.notify()

    def get(self):
        with self.not_empty:
            while not self.items:
                self.not_empty.wait()
            item = self.items.pop(0)
            # print(f"Item Popped from queue: {item}")
            self.not_empty.notify()
            return item

