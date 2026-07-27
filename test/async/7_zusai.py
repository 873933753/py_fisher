# async 函数里只用 async 库（asyncio.sleep、aiohttp 等）

# 测试 time.sleep 和 asyncio.sleep 的执行顺序
# time.sleep 是同步阻塞，卡住整个事件循环
# asyncio.sleep 是异步等待，不阻塞


import asyncio
import time


async def bad_task(name):
    print(f"  {name} 开始")
    time.sleep(1)  # ❌ 同步阻塞！卡住整个事件循环
    print(f"  {name} 结束")


async def good_task(name):
    print(f"  {name} 开始")
    await asyncio.sleep(1)  # ✅ 异步等待，不阻塞
    print(f"  {name} 结束")


async def main():
    print("=== 用 time.sleep（错误示范）===")
    start = time.time()
    await asyncio.gather(bad_task("A"), bad_task("B"))
    print(f"耗时: {time.time() - start:.2f} 秒\n")

    print("=== 用 asyncio.sleep（正确）===")
    start = time.time()
    await asyncio.gather(good_task("C"), good_task("D"))
    print(f"耗时: {time.time() - start:.2f} 秒")


asyncio.run(main())


""" 
=== 用 time.sleep（错误示范）===
  A 开始
  A 结束
  B 开始
  B 结束
耗时: 2.00 秒        ← gather 失效了！变成顺序执行

=== 用 asyncio.sleep（正确）===
  C 开始
  D 开始
  C 结束
  D 结束
耗时: 1.00 秒        ← 真正的并发
"""
