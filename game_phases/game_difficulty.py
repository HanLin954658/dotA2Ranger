# game_phases/difficulty.py
import time
from loguru import logger


class DifficultyPhase:
    def __init__(self, state_manager, km_controller, vision_processor, config):
        self.state_manager = state_manager
        self.km = km_controller
        self.vision = vision_processor
        self.difficulty_level = config.get("difficulty", 6) - 1

    def execute(self):
        self.state_manager.wait_until_resumed()
        logger.info("开始执行难度选择阶段")

        while True:
            x, y, conf = self.vision.find_text("开始游戏", 1649, 939, 1819, 995)
            if x > 0:
                difficulty_y = 291 + self.difficulty_level * 53
                logger.info(f"选择难度级别: {self.difficulty_level + 1}")
                self.km.move_and_click(953, difficulty_y, 3)
                self.km.move_and_click(x, y, 2)
                break
            time.sleep(5)
        logger.info("难度选择阶段完成")