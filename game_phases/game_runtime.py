# game_phases/collapse.py
import time
from loguru import logger
from game_components.item_manager import ItemManager


class CollapsePhase:
    def __init__(self, state_manager, km_controller, vision_processor, config):
        self.state_manager = state_manager
        self.km = km_controller
        self.vision = vision_processor
        self.config = config
        self.shenji_times = 0
        self.item_manager = ItemManager(state_manager, km_controller, vision_processor)

    def execute(self):
        self.state_manager.wait_until_resumed()
        logger.info("开始执行资源收集阶段")

        investment_toggled = True
        taxia_performed = False
        FIND_TEXT_TIMEOUT = 60

        while True:
            curr, exec_time_sec = self.vision.get_run_time()
            if exec_time_sec < 60 and investment_toggled:
                self._toggle_investment()
                investment_toggled = False

            x, y, conf = self.vision.find_text("收起", 700, 706, 1145, 925)
            if x > 0:
                logger.info(f"找到'收起'按钮 - 坐标: ({x}, {y}), 置信度: {conf:.2f}, 准备点击")
                self.km.move_and_click(x, y, 2)
                time.sleep(1)
                break

            self._perform_common_operations(exec_time_sec,curr)

            if not investment_toggled and exec_time_sec > FIND_TEXT_TIMEOUT:
                self._handle_investment_timeout(investment_toggled)
                investment_toggled = True

            if not taxia_performed and exec_time_sec > 900:
                self._perform_special_operations()
                taxia_performed = True

            if self.config.get("useMoney", True):
                self._handle_skill_upgrades()

            time.sleep(5)

        logger.info(f"资源收集阶段完成，总耗时: {exec_time_sec} 秒")

    def _toggle_investment(self):
        if not self.config.get("useMoney", True):
            return
        logger.info("切换投资状态")
        self.km.right_click(806, 976, 1)
        self.km.press_key('A')
        self.km.move_and_click(948, 527)

    def _perform_common_operations(self, exec_time_sec,curr):
        self.km.press_key('f1', 1, 0.1)
        self.km.press_key('a')
        self.km.move_and_click(963, 525)
        self.km.move_and_click(963, 525)
        logger.info(f"已执行 {exec_time_sec:.2f} 秒，当前运行时间{curr}")

    def _handle_investment_timeout(self, exec_time_sec):
        logger.info(f"已执行 {exec_time_sec:.2f} 秒，超过查找按钮超时时间，切换投资状态")
        self._toggle_investment()

    def _perform_special_operations(self):
        logger.info("准备执行特定操作")
        self.km.move_to_position(73, 911, 707, 420)
        time.sleep(15)
        self.km.press_key('f2', 1)
        self.km.move_to_position(88, 932, 910, 595)

    def _handle_skill_upgrades(self):
        if self.shenji_times < 8:
            self.km.move_and_click(878, 991)
            # ...（保持原有技能升级逻辑）
        self.km.press_key("f1", 2, 0.1)
        self.km.press_key('a')
        self.km.move_and_click(963, 525)
        self.km.move_and_click(947, 982)
        self.km.move_and_click(1034, 978)
        self.km.move_and_click(770, 551, 3)
        self.km.move_and_click(1066, 634, 3)