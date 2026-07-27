# 多线程

import threading
import time

""" 
将子线程代码写在主线程前
"""


# 定义子线程函数
def print_hello():
    print("Hello, World!")
    # 获取当前线程名称
    t = threading.current_thread()
    time.sleep(100)  # 等待100秒，看子线程是否执行
    print(t.name)


# 不创建子线程，直接睡眠100秒
time.sleep(100)

# 主线程
print("主线程开始")

# 获取当前线程名称
t = threading.current_thread()
print(t.name)


""" 
打印结果：
100s后打印：
主线程开始
MainThread
 """
