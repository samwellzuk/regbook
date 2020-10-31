# -*-coding: utf-8 -*-
# Created by samwell
import threading


class Singleton(type):
    """
    metaclass 实现了多线程单体模式
    注意：metaclass 对于每个目标类实际上都要初始化一个对象，因此锁和instance都是按目标类创建的，即单体类的cls,即该目标类
    """

    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        cls.__lock = threading.Lock()
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = super().__call__(*args, **kwargs)
                return cls.__instance
            else:
                return cls.__instance
