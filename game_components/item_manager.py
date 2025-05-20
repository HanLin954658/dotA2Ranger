"""
Game item management for automation.
"""
from loguru import logger

from utils.vision_processor import VisionProcess
from utils.state_manager import StateManager
from utils.km_controller import KMController



class ItemManager:
    """
    Manages item usage and related functions.
    """

    def __init__(self, state_manager: StateManager,
                 mouse_controller: KMController,
                 vision_processor: VisionProcess
                 ):
        """Initialize item manager."""
        self.state_manager = state_manager
        self.km = mouse_controller
        self.vision = vision_processor

    def use_items(self):
        """Use items function."""
        self.state_manager.wait_until_resumed()
        logger.info("Starting to use items")

        for i in range(20):
            self.km.press_key("f1")
            # Look for upgrade button
            x, y = self.vision.find_image(
                "images/shengji.bmp", 1142, 931, 1372, 1064
            )
            if x > 0:
                self.km.move_and_click(x, y)
                # Look for attack speed
                x_gs, y_gs,conf_gs = self.vision.find_text(
                    "攻击速度", 803, 335, 1075, 591
                )
                if x_gs > 0:
                    logger.info("Found attack speed")
                    self.km.move_and_click(x_gs, y_gs, 2)
                    continue
                # Click default position
                self.km.move_and_click(898, 561, 2)
                continue

            # Look for jueze button
            x, y = self.vision.find_image(
                "images/jueze.bmp", 1142, 931, 1372, 1064
            )
            if x > 0:
                self.km.move_and_click(x, y)
                x_sm, y_sm, conf_sm = self.vision.find_text("生命值", 713, 371, 789, 563)
                if x_sm > 0:
                    self.km.move_and_click(x_sm, y_sm)
                    continue
                x_sm, y_sm, conf_sm = self.vision.find_text("生命值", 907, 368, 976, 567)
                if x_sm > 0:
                    self.km.move_and_click(x_sm, y_sm)
                    continue

                self.km.move_and_click(898, 561, 2)
                continue
            # Look for shenhua button
            x, y = self.vision.find_image(
                "images/shenhua.bmp", 1142, 931, 1372, 1064
            )
            if x > 0:
                self.km.move_and_click(x, y)

                x_sm,  y_sm,conf_sm = self.vision.find_text("生命值", 835, 361, 986,565)
                if x_sm > 0:
                    self.km.move_and_click(x_sm, y_sm)
                    continue
                x_sm, y_sm, conf_sm = self.vision.find_text("生命恢复", 835, 361, 986,565)
                if x_sm > 0:
                    self.km.move_and_click(x_sm, y_sm)
                    continue
                self.km.move_and_click(898, 561, 2)
                continue

            # Look for quanneng button
            x, y = self.vision.find_image(
                "images/quanneng.bmp", 1142, 931, 1372, 1064
            )
            if x > 0:
                self.km.move_and_click(x, y)
                continue
            # All complete
            break
