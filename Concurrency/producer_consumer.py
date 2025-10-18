import queue
import threading
import time
import simple_blocking_queue

# q = queue.Queue(maxsize=6)
q = simple_blocking_queue.SimpleBlockingQueue(max_size=2)


def producer():
    for i in range(10):
        print(f"Produce {i}")
        # print(q.unfinished_tasks)
        q.put(i)
        # print(q.queue)
        time.sleep(2)
    # print(q.unfinished_tasks)


def consumer():
    while True:
        item = q.get()
        print(f"Consumed {item}")
        time.sleep(5)
        # q.task_done()


threading.Thread(target=producer).start()
threading.Thread(target=consumer).start()
