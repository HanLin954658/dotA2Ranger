# game_phases/restart.py
import time
from loguru import logger


class RestartPhase:
    def __init__(self, state_manager, km_controller):
        self.state_manager = state_manager
        self.km = km_controller

    def execute(self):
        self.state_manager.wait_until_resumed()
        logger.info("开始执行游戏重开阶段")
        logger.debug("点击游戏菜单按钮")
        self.km.press_key('F1', 2)
        self.km.press_key('F2')
        time.sleep(1)
        logger.info("开始执行重开操作")
        self.km.move_and_click(1068,913, 2)
        logger.debug("确认重开游戏")
        time.sleep(1)
        self.km.move_and_click(823, 624, 2, 1)

        logger.info("游戏重开阶段完成")



