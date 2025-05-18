import pyautogui
import time
from loguru import logger

from utils.state_manager import StateManager


class MouseController:
    def __init__(self):
        self.state_manager=StateManager()


    def move_and_click(self, x, y, clicks=1, interval=0.2):
        """移动到指定位置并点击"""
        self.state_manager.wait_until_resumed()
        if x < 0 or y < 0:
            logger.info("坐标错误")
            return

        pyautogui.moveTo(x, y, duration=0.1)
        time.sleep(0.1)
        pyautogui.click(clicks=clicks, interval=interval)
        time.sleep(0.1)

    def press_key(self, key, presses=1, interval=0.5):
        """按下指定按键"""
        for _ in range(presses):
            pyautogui.press(key)
            time.sleep(interval)