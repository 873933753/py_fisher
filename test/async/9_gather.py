import asyncio


# 测试 gather 的异常处理
# 情况1：某个任务失败，gather 默认会抛异常
# 情况2：return_exceptions=True，异常作为结果返回


async def ok_task():
    await asyncio.sleep(0.5)
    return "成功"


async def fail_task():
    await asyncio.sleep(0.5)
    raise ValueError("出错了！")


async def main():
    # 情况1：某个任务失败，gather 默认会抛异常
    try:
        await asyncio.gather(ok_task(), fail_task())
    except ValueError as e:
        print(f"gather 捕获异常: {e}")

    # 情况2：return_exceptions=True，异常作为结果返回
    results = await asyncio.gather(
        ok_task(),
        fail_task(),
        return_exceptions=True,
    )
    print("结果:", results)
    print("第2个是异常吗?", isinstance(results[1], ValueError))


asyncio.run(main())
