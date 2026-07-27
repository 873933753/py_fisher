class MyResource:
    def __enter__(self):
        print("Entering the resource...")
        return self

    # __exit__方法的参数是exc_type, exc_value, traceback
    # 分别是异常类型，异常值，异常追踪
    # 如果异常发生，则exc_type, exc_value, traceback不为None
    # 如果异常没有发生，则exc_type, exc_value, traceback为None
    def __exit__(self, exc_type, exc_value, tb):
        # 这里是在exit方法中处理异常
        if tb:
            print("process exception")
        else:
            print("no exception")
        print("Exiting the resource...")
        # 返回True表示异常被处理，False表示异常未被处理，不返回则默认False - 通知上级with语句异常被处理，不用再处理
        # 如果返回False，则上级with语句会再次处理异常
        return True

    def query(self):
        print("query data")


""" 
  1）进入with语句调用__enter__方法
  2）enter方法返回的值赋值给as后面的变量resource
  3）enter执行完执行with中的代码 resource.query()
  4）with中的代码执行完调用__exit__方法
  5）exit方法执行完释放资源
"""


# 使用try-except语句处理异常
# 如果exit方法返回True，则异常被处理，不会进入except语句
# 如果exit方法返回False，则异常未被处理，会进入except语句
try:
    # with 语句会自动调用 __enter__ 和 __exit__ 方法
    # 所以 __enter__ 方法返回的值会赋值给 as 后面的变量
    with MyResource() as resource:
        # 这里可能会抛出异常
        # 这里抛出异常进入__exit__ /
        # 使用资源 resource
        resource.query()
except Exception as e:
    pass
