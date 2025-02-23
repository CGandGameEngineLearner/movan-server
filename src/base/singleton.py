from threading import Lock

def singleton(cls):
    instances = {}  # 存储类与实例的映射
    lock = Lock()   # 线程同步锁
    
    def wrapper(*args, **kwargs):
        # 第一层检查：无锁快速路径
        if cls not in instances:  # 避免已存在实例时获取锁
            with lock:  # 进入同步代码块
                # 第二层检查：防止多个线程同时通过第一层检查
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)  # 真正的实例化
        return instances[cls]
    return wrapper

if __name__ == "__main__":
    # 基础用法
    @singleton  # 添加装饰器
    class AppConfig:
        def __init__(self):
            self.settings = {"debug": False}
            
    # 多线程测试
    import threading

    def test_singleton():
        config = AppConfig()
        config.settings["thread"] = threading.current_thread().name
        print(id(config))

    # 启动10个线程
    threads = []
    for _ in range(10):
        t = threading.Thread(target=test_singleton)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # 输出结果：所有打印的id相同