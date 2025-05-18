# state_manager.py
import time

import winsound
from loguru import logger

class StateManager:
    def __init__(self):
        self.paused = False

    def toggle_pause(self):
        """切换脚本暂停状态"""
        winsound.Beep(2000, 500)
        self.paused = not self.paused
        status = "已暂停" if self.paused else "已恢复"
        logger.info(f"脚本状态: {status}")
        return self.paused

    def is_paused(self):
        """检查脚本是否暂停"""
        return self.paused

    def wait_until_resumed(self):
        """等待脚本恢复运行"""
        if self.is_paused():
            winsound.Beep(1000, 500)
        while self.is_paused():
            if int(time.time()) % 10 == 0:
                logger.info("脚本暂停中")
            time.sleep(1)

# 创建单例实例
state_manager = StateManager()