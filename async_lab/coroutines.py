import asyncio


async def inner():
    print("inner: start")
    await asyncio.sleep(1)
    print("inner: end")
    return "done"


async def outer():
    print("outer: before await")
    result = await inner()
    print("outer: after await, got:", result)


asyncio.run(outer())