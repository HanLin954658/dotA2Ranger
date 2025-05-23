import time

from loguru import logger
from utils.km_controller import KMController
from utils.state_manager import StateManager
from utils.vision_processor import VisionProcess


class ArchiveProcess:
    def __init__(self, config, state_manager, vision_processor, km_controller):
        self.config = config
        self.state_manager = state_manager
        self.vision = vision_processor
        self.km = km_controller

    def execute(self):
        self.state_manager.wait_until_resumed()
        logger.info("开始执行游戏存档阶段")
        self.battle_royal()


    def battle_royal(self):
        self.km.press_key('F2')
        self.km.move_and_click(1076,603  )
        time.sleep(1)
        self.km.move_and_click(832,625)
        time.sleep(1)
        self.km.move_a_to_target_position(0,0,962,521)
        for i in range(50):
            x, y, conf = self.vision.find_text("确定", 871, 847, 1051, 895)
            time.sleep(6)
            if x > 0:
                result_list = self.vision.get_all_coordinates_and_text(497, 195, 1367, 733)
                for result in result_list:
                    if '铜币' in result[2]:
                        self.km.move_and_click(result[0], result[1])
                for result in result_list:
                    if '阶' in result[2]:
                        self.km.move_and_click(result[0], result[1])

                self.km.move_and_click(x, y, 2)
                break
            time.sleep(3)


        self.km.press_key('F2',2)
