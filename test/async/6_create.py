import asyncio
import time

# 测试 create_task 和 gather 的执行顺序
# create_task 是立刻提交给事件循环，gather 是一次性提交并等待全部
# 任务在 create_task() 时就已开始执行，你可以选择何时 await 获取结果


async def work(name, sec):
    print(f"  {name} 启动")
    await asyncio.sleep(sec)
    print(f"  {name} 完成")
    return name


async def main():
    start = time.time()

    # 方式A：create_task — 立刻提交给事件循环
    print("--- create_task ---")
    t1 = asyncio.create_task(work("任务1", 2))
    t2 = asyncio.create_task(work("任务2", 1))
    # 注意：上面两行之后，两个任务已经在后台跑了！
    print("  两个任务已提交，main 继续干别的事...")
    await asyncio.sleep(0.5)
    print("  main 等了 0.5 秒，现在去收结果")

    # 通过await来获取结果
    r1 = await t1
    r2 = await t2
    print(f"  结果: {r1}, {r2}")
    print(f"  耗时: {time.time() - start:.2f} 秒\n")

    # 方式B：gather — 一次性提交并等待全部
    start = time.time()
    print("--- gather ---")
    results = await asyncio.gather(
        work("任务3", 2),
        work("任务4", 1),
    )
    print(f"  结果: {results}")
    print(f"  耗时: {time.time() - start:.2f} 秒")


asyncio.run(main())
