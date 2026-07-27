import asyncio

# await：当前任务等这一个做完，再往下走。
# gather：一起开始，等全部完成


async def task(name, seconds):
    print(f"  [{name}] 开始，要等 {seconds} 秒")
    await asyncio.sleep(seconds)
    print(f"  [{name}] 结束")


async def main():
    print("=== 顺序执行（一个接一个）===")
    await task("A", 1)  # 顺序执行，A结束才能执行B
    # await要等待task("A", 1)结束才能执行task("B", 1)
    await task("B", 1)
    print("顺序执行完毕\n")

    print("=== 并发执行（同时开始）===")
    await asyncio.gather(
        task("C", 1),  # 并发执行，C和D同时开始，同时结束
        task("D", 1),
    )
    print("并发执行完毕")


asyncio.run(main())

""" 
执行结果：
=== 顺序执行（一个接一个）===
  [A] 开始，要等 1 秒
  [A] 结束
  [B] 开始，要等 1 秒
  [B] 结束
顺序执行完毕

=== 并发执行（同时开始）===
  [C] 开始，要等 1 秒
  [D] 开始，要等 1 秒
  [C] 结束
  [D] 结束
并发执行完毕
"""
