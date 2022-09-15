import asyncio
import time


async def task(t):
    await asyncio.sleep(t)
    print("hello", t)


async def main():
    t1 = task(1)
    t2 = task(2)
    t3 = task(3)

    await asyncio.gather(t1, t2, t3)


if __name__ == '__main__':
    t0 = time.time()
    asyncio.run(main())
    print(time.time() - t0)
