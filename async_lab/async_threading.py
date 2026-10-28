
import time
import httpx
import threading

def make_request():
    start = time.perf_counter()
    response = httpx.get("http://127.0.0.1:5001/nutrition/eggs")
    elapsed = time.perf_counter() - start
    print(f"Request finished: {response.status_code}, {elapsed:.4f} seconds")

def run_threaded():
    threads = []
    start = time.perf_counter()

    for _ in range(3):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(f"Total threaded time: {time.perf_counter() - start:.4f} seconds")

run_threaded()
