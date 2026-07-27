# 多线程

import threading
import time

""" 
将子线程代码写在主线程前
线程之间是并发执行的，而不是顺序执行的
所以子线程中的代码并不会阻塞主线程
但是主线程中的代码会阻塞子线程
"""


# 定义子线程函数
def print_hello():
    print("Hello, World!")
    # 获取当前线程名称
    t = threading.current_thread()
    time.sleep(100)  # 等待100秒，看子线程是否执行
    print(t.name)


# 创建子线程
t2 = threading.Thread(target=print_hello, name="子线程1")
t2.start()  # 启动子线程

# 主线程
print("主线程开始")

# 获取当前线程名称
t = threading.current_thread()
print(t.name)


""" 
打印结果：
Hello, World! - 说明子线程中的代码并wei
主线程开始
MainThread
子线程1（睡眠100秒），但是如果没启子线程直接睡眠100s，是会阻塞主线程的
 """
