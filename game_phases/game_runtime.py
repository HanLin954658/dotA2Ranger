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
            # 位置复位
            self.km.return_to_initial_position()

            # 关闭投资
            if not investment_toggled and exec_time_sec > FIND_TEXT_TIMEOUT:
                self._handle_investment_timeout(investment_toggled)
                investment_toggled = True
            # 前往塔下
            if not taxia_performed and exec_time_sec > 1000:
                self._perform_special_operations()
                self.shenji_times = 0
                taxia_performed = True
            # 停止操作
            if exec_time_sec < 1000:
                if self.config.get("useMoney", True):
                    self._handle_skill_upgrades()
                self.km.move_and_click(1872, 341, 5)
                # 使用道具
                self.item_manager.use_items()

                time.sleep(5)

        logger.info(f"资源收集阶段完成，总耗时: {exec_time_sec} 秒")

    def _toggle_investment(self):
        if not self.config.get("use_gold", True):
            return
        logger.info("切换投资状态")
        self.km.right_click(806, 976, 1)
        self.km.return_to_initial_position()
    # 返回初始位置

    def _handle_investment_timeout(self, exec_time_sec):
        logger.info(f"已执行 {exec_time_sec:.2f} 秒，超过查找按钮超时时间，切换投资状态")
        self._toggle_investment()

    def _perform_special_operations(self):
        logger.info("准备前往塔下")
        self.km.move_to_position(73, 911, 707, 420)
        time.sleep(30)
        self.km.return_to_initial_position()

    def _handle_skill_upgrades(self):
        if self.shenji_times < 8:
            self.km.move_and_click(878, 991)
            # "", "", "3W敌法", "再生之力", "", "琉璃大炮", "",
            # "", "生命膨胀", "攻击强化",, "召唤", , "血之箭",
            # "浸毒武器", "小小之心", "剧毒体质", "多重射击", "毒液外衣",
            #
            # "极速箭术", "月神箭", "生命膨胀", "召唤", "血之箭", "琉璃大炮", "小金库", "百步穿杨"
            texts_to_find = ["极速箭术", "月神箭", "暴击强化", "生命膨胀",
                             "血之箭","琉璃大炮", "小金库", "百步穿杨",
                             "献祭","多重射击", "浸毒武器", "剧毒体质",
                             "死亡之舞", "黄金剑","自愈之力"]  # 替换为实际需要检测的文本内容
            time.sleep(1)
            x, y, conf = self.vision.find_text("刷新", 775, 758, 1095, 855)  # 根据实际区域调整坐标范围
            if x > 0:
                self.shenji_times += 1
                logger.info(f"神技升级次数：{self.shenji_times}")
                for text in texts_to_find:
                    x, y, conf = self.vision.find_text(text, 512, 442, 1398, 525)  # 根据实际区域调整坐标范围
                    if x > 0:
                        logger.info(f"找到文本 '{text}'，准备点击")
                        self.km.move_and_click(x, y)
                        break
                else:
                    self.km.move_and_click(770, 551, 1)

        self.km.return_to_initial_position()
        logger.debug("执行转世操作")
        self.km.move_and_click(947, 982)
        self.km.move_and_click(1034, 978)
        logger.debug("执行转世操作")
        self.km.move_and_click(770, 551, 1)
        self.km.move_and_click(1066, 634, 1)
        logger.info("技能升级和转世操作完成")