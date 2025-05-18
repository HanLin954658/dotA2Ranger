# state_manager.py
import threading
import time

import winsound
from loguru import logger

class StateManager:
    _instance = None  # 类变量存储单例
    _lock = threading.Lock()  # 类级线程锁

    def __new__(cls):
        """重写 __new__ 实现单例"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化仅执行一次"""
        if not self._initialized:
            self._paused = False
            self._init_lock = threading.Lock()  # 实例级锁
            self._initialized = True

    def toggle_pause(self) -> bool:
        """切换暂停状态（线程安全）"""
        with self._init_lock:
            self._paused = not self._paused
            status = "已暂停" if self._paused else "已恢复"
            winsound.Beep(2000 if self._paused else 1000, 500)
            logger.info(f"脚本状态: {status}")
            return self._paused

    def is_paused(self) -> bool:
        """获取当前状态（线程安全）"""
        with self._init_lock:
            return self._paused

    def wait_until_resumed(self) -> None:
        """阻塞直到脚本恢复（每10秒提示）"""
        while self.is_paused():
            if int(time.time()) % 10 == 0:
                logger.info("脚本暂停中")
            time.sleep(1)