import asyncio
import time

async def one():
    print("one: A")
    time.sleep(1)
    print("one: B")

async def two():
    print("two: A")
    await asyncio.sleep(1)
    print("two: B")

async def main():
    print("main: start")
    await one()
    await two()
    print("main: end")

asyncio.run(main())

async def inner():
    print("inner: before sleep")
    await asyncio.sleep(1)
    print("inner: after sleep")

async def friend():
    print("friend: before sleep")
    await asyncio.sleep(1)
    print("friend: after sleep")

async def main():
    print("main: start")
    await inner()
    await friend()
    print("main: end")

asyncio.run(main())




async def one():
    print("one: A")
    await asyncio.sleep(1)
    print("one: B")

async def two():
    print("two: A")
    await asyncio.sleep(1)
    print("two: B")

async def main():
    print("main: start")
    await one()
    await two()
    print("main: end")

asyncio.run(main())

