import asyncio

# 测试 gather 返回结果的顺序
# 返回列表顺序 = 传入顺序（不是完成顺序）！！！


async def fetch(name, delay):
    await asyncio.sleep(delay)
    print(f"{name} 完成")
    return f"{name} 的数据"


async def main():
    # gather 返回结果列表，顺序与传入顺序一致
    results = await asyncio.gather(
        fetch("苹果", 2),
        fetch("香蕉", 1),
        fetch("橙子", 3),
    )
    # 返回列表顺序 = 传入顺序（不是完成顺序）！！！
    print("结果:", results)
    print("类型:", type(results))


asyncio.run(main())

""" 
香蕉 完成
苹果 完成
橙子 完成
结果: ['苹果 的数据', '香蕉 的数据', '橙子 的数据']
类型: <class 'list'>
"""
