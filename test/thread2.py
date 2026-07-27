# 多线程

import threading

# 主线程
print("主线程开始")

# 获取当前线程名称
t = threading.current_thread()
print(t.name)


# 定义子线程函数
def print_hello():
    print("Hello, World!")
    # 获取当前线程名称
    t = threading.current_thread()
    print(t.name)


# 创建子线程
t2 = threading.Thread(target=print_hello, name="子线程1")
t2.start()  # 启动子线程


""" 
打印结果：
主线程开始
MainThread
Hello, World!
子线程1
 """
