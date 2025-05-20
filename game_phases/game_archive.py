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
        time.sleep(120)
        for  i in range(5):
            for  j in range(2):
                self.km.move_and_click(604+i*150,281+j*160)
                time.sleep(1)
        self.km.move_and_click(976,862  )
        self.km.press_key('F2',2)
