import asyncio
import time

# 验证顺序和并发的耗时


async def sleep_task(name, sec):
    print(f"  {name} 开始")
    await asyncio.sleep(sec)
    print(f"  {name} 结束")


async def main():
    # --- 测试1：顺序 ---
    start = time.time()
    await sleep_task("顺序-A", 1)
    await sleep_task("顺序-B", 1)
    await sleep_task("顺序-C", 1)
    print(f"顺序耗时: {time.time() - start:.2f} 秒\n")

    # --- 测试2：并发 ---
    start = time.time()
    await asyncio.gather(
        sleep_task("并发-A", 1),
        sleep_task("并发-B", 1),
        sleep_task("并发-C", 1),
    )
    print(f"并发耗时: {time.time() - start:.2f} 秒")


asyncio.run(main())

""" 
执行结果：
  顺序-A 开始
  顺序-A 结束
  顺序-B 开始
  顺序-B 结束
  顺序-C 开始
  顺序-C 结束
顺序耗时: 3.00 秒

  并发-A 开始
  并发-B 开始
  并发-C 开始
  并发-A 结束
  并发-B 结束
  并发-C 结束
并发耗时: 1.00 秒
"""
