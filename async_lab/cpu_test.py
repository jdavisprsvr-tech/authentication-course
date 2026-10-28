import time

def count_up(n):
    total = 0
    for i in range(n):
        total += i
    return total
n = 5_000_000
start = time.perf_counter()
count_up(n)
count_up(n)
count_up(n)

print(f"Sequential time: {time.perf_counter() - start:.4f} seconds")

import time
import threading

def count_up(n):
    total = 0
    for i in range(n):
        total += i
    return total
n = 5_000_000
runs = 3

sequential_times = []
threaded_times = []

for run in range(runs):
    start = time.perf_counter()
    count_up(n)
    count_up(n)
    count_up(n)

    elapsed = time.perf_counter() - start
    sequential_times.append(elapsed)
    print(f"Sequential run {run + 1}: {elapsed:.4f} seconds")
for run in range(runs):
    threads = []
    start = time.perf_counter()
    for _ in range(3):
        thread = threading.Thread(target=count_up, args=(n,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    elapsed = time.perf_counter() - start
    threaded_times.append(elapsed)
    print(f"Threaded run {run + 1}: {elapsed:.4f} seconds")
sequential_avg = sum(sequential_times) / runs
threaded_avg = sum(threaded_times) / runs
print("\n--- Final Comparison ---")
print(f"Sequential average: {sequential_avg:.4f} seconds")
print(f"Threaded average:   {threaded_avg:.4f} seconds")
if sequential_avg < threaded_avg:
    print("Sequential was faster.")
elif threaded_avg < sequential_avg:
    print("Threaded was faster.")
else:
    print("Both averaged the same time.")
