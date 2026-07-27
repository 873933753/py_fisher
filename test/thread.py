# 多线程

import threading

# 主线程
print("主线程开始")

# 获取当前线程名称
t = threading.current_thread()
print(t.name)

""" 
打印结果：
主线程开始
MainThread
 """
