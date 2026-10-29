import asyncio
import time


async def worker(name, delay):
    await asyncio.sleep(delay)
    return name

# asyncio.gather is analogous to JavaScript Promise.all,
# but Python coroutine calls are inactive until awaited or scheduled.
async def main():
    task1 = asyncio.create_task(worker("first", 1))
    task2 = asyncio.create_task(worker("second", 2))
    task3 = asyncio.create_task(worker("third", 3))

    start = time.perf_counter()

    results = await asyncio.gather(task1, task2, task3)
    
    end = time.perf_counter()

    print("Results:", results)
    print("Elasped time:", end - start)

asyncio.run(main())


async def main_sequential():
    start = time.perf_counter()
    a = await worker("first", 1)
    b = await worker("second", 2)
    c = await worker("third", 3)
    end = time.perf_counter()
    results = [a, b, c]

    print("Sequential results:", results)
    print("Sequential elasped time:", end - start)

asyncio.run(main_sequential())