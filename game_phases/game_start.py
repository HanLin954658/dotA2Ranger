# game_phases/game_start.py
import time
from loguru import logger


class GameStartPhase:
    def __init__(self, state_manager, km_controller, vision_processor):
        self.state_manager = state_manager
        self.km = km_controller
        self.vision = vision_processor

    def execute(self):
        self.state_manager.wait_until_resumed()
        logger.info("开始执行游戏启动阶段")

        while True:
            run_time, run_time_sec = self.vision.get_run_time(x1=897, y1=0, x2=1015, y2=27, scale=2)
            if 0 < run_time_sec < 60:
                logger.debug("移动到游戏界面初始位置")
                self.km.move_to_position(90, 943, 939, 267)
                break
            logger.debug(f"当前时间为{run_time},不符合开局要求")
            time.sleep(3)
        logger.info("游戏启动阶段完成")