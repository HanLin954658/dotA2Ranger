import time
from typing import Dict, Any
from loguru import logger
from utils.state_manager import StateManager
from utils.km_controller import KMController
from utils.vision_processor import VisionProcess
from game_components.item_manager import ItemManager


class GamePhaseManager:
    """
    管理游戏自动化的不同阶段，包括游戏启动、资源收集、重开和难度选择等操作。
    """

    def __init__(self, state_manager: StateManager,
                 km_controller: KMController,
                 vision_processor: VisionProcess,
                 config: Dict[str, Any]):
        """
        初始化游戏阶段管理器。

        Args:
            state_manager: 状态管理器，控制游戏自动化的暂停和恢复
            km_controller: 键盘鼠标控制器，执行游戏中的交互操作
            vision_processor: 视觉处理器，识别游戏中的文本和图像
            config: 游戏配置，包含难度级别、是否使用资源等设置
        """
        self.state_manager = state_manager
        self.km = km_controller
        self.vision = vision_processor
        self.config = config
        self.shenji_times = 0
        # 初始化物品管理器
        self.item_manager = ItemManager(
            state_manager, km_controller, vision_processor
        )

        # 配置值
        self.difficulty_level = config.get("nandu", 6) - 1
        self.use_money = config.get("useMoney", True)
        logger.info(f"游戏配置加载完成 - 难度级别: {self.difficulty_level + 1}, 使用资源: {self.use_money}")

    def handle_game_start(self):
        """
        处理游戏启动阶段，等待用户恢复脚本运行后，定位并点击"普通模式"按钮进入游戏。
        """
        self.state_manager.wait_until_resumed()
        logger.info("开始执行游戏启动阶段")
        logger.debug("正在查找'普通模式'按钮")

        while True:

            run_time,run_time_sec = self.vision.get_run_time(x1=897, y1=0, x2=1015, y2=27, scale=2)
            if 0 < run_time_sec < 60:
                logger.debug("移动到游戏界面初始位置")
                self.km.move_to_position(90,943, 939,267 )
                break
            logger.debug(f"当前时间为{run_time},不符合开局要求")
            time.sleep(3)
        logger.info("游戏启动阶段完成")

    def handle_collapse(self):
        """
        处理资源收集阶段，执行自动收集、投资切换和技能升级等操作。
        包含超时处理机制，确保在不同情况下采取适当的操作。
        """
        self.state_manager.wait_until_resumed()
        logger.info("开始执行资源收集阶段")


        # 状态跟踪
        investment_toggled = True
        taxia_performed = False
        self.shenji_times = 0
        # 超时设置
        FIND_TEXT_TIMEOUT = 180  # 查找"收起"按钮的超时时间(秒)

        logger.debug("开始资源收集循环")
        while True:
            # 计算已执行时间
            curr,exec_time_sec = self.vision.get_run_time()
            if exec_time_sec < 60 and investment_toggled:
                self._toggle_investment()
                investment_toggled = False
            logger.info(f"已执行 {exec_time_sec:.2f} 秒，当前运行时间{curr}")
            # 查找"收起"按钮
            x, y, conf = self.vision.find_text(
                "收起", 700, 706, 1145, 925
            )
            self.km.press_key('f1', 3,0.1)  # 刷新界面
            self.km.press_key('a')
            self.km.move_and_click(963, 525)
            if x > 0:
                logger.info(f"找到'收起'按钮 - 坐标: ({x}, {y}), 置信度: {conf:.2f}, 准备点击")
                self.km.move_and_click(x, y, 2)
                time.sleep(1)
                break

            # 超时后切换投资
            if not investment_toggled and exec_time_sec > FIND_TEXT_TIMEOUT:
                logger.info(f"已执行 {exec_time_sec:.2f} 秒，超过查找按钮超时时间，切换投资状态")
                self._toggle_investment()
                investment_toggled = True

            # 执行特定操作
            if not taxia_performed and exec_time_sec > 900:
                logger.info(f"已执行 {exec_time_sec:.2f} 秒，准备执行特定操作")
                self.km.move_to_position(73,911, 707,420)
                time.sleep(15)
                self.km.press_key('f2', 1)
                self.km.move_to_position(88,932, 910,595)
                taxia_performed = True

            # 在时间限制内使用物品
            if exec_time_sec < 900:  # 提前结束以避免与特定操作冲突
                self.item_manager.use_items()

            # 执行技能升级和转世
            if self.use_money:
                self._skill_and_reincarnation()
                # 挑战升级
                self.km.move_and_click(1880,354,3)

            # 循环间隔
            time.sleep(5)

        logger.info(f"资源收集阶段完成，总耗时: {exec_time_sec} 秒")

    def handle_restart(self):
        """
        处理游戏重开阶段，执行重开游戏的一系列操作，包括点击重开按钮和确认操作。
        """

        while True:
            self.state_manager.wait_until_resumed()
            logger.info("开始执行游戏重开阶段")

            logger.debug("点击游戏菜单按钮")
            self.km.move_and_click(112, 955)
            time.sleep(1)

            logger.debug("查找'重开游戏'按钮")
            x, y, conf = self.vision.find_text(
                "重开游戏", 809, 565, 905, 597
            )
            if x > 0:
                logger.info(f"找到'重开游戏'按钮 - 坐标: ({x}, {y}), 置信度: {conf:.2f}")
                logger.info("开始执行重开操作")
                self.km.move_and_click(x, y, 2)
                logger.debug("确认重开游戏")
                time.sleep(1)
                self.km.move_and_click(823,624, 2,1)
                break

            logger.debug("未找到'重开游戏'按钮，继续等待...")
            time.sleep(5)
        logger.info("游戏重开阶段完成")

    def handle_difficulty(self):
        """
        处理难度选择阶段，根据配置选择相应难度并开始游戏。
        """
        self.state_manager.wait_until_resumed()
        logger.info("开始执行难度选择阶段")

        logger.debug("查找'开始游戏'按钮")
        while True:
            x, y, conf = self.vision.find_text(
                "开始游戏", 1649, 939, 1819, 995
            )
            logger.debug(f"当前难度级别配置: {self.difficulty_level + 1}")
            if x > 0:
                # 计算难度位置
                difficulty_y = 291 + self.difficulty_level * 53
                logger.info(f"选择难度级别: {self.difficulty_level + 1}")
                self.km.move_and_click(953, difficulty_y, 3)
                logger.info(f"点击'开始游戏'按钮 - 坐标: ({x}, {y})")
                self.km.move_and_click(x, y, 2)
                break
            logger.debug("未找到'开始游戏'按钮，继续等待...")
            time.sleep(5)
        logger.info("难度选择阶段完成")

    def _toggle_investment(self):
        """
        切换投资功能，通过右键点击特定位置实现。
        如果未启用资源消耗，则跳过此操作。
        """
        if not self.use_money:
            logger.info("未启用资源消耗，跳过投资切换")
            return

        logger.info("切换投资状态")
        self.km.right_click(806, 976, 1)
        logger.debug("投资状态切换完成")

    def _skill_and_reincarnation(self):
        """
        升级技能和执行转世功能，点击多个位置完成技能升级和转世操作。
        如果未启用资源消耗，则跳过此操作。
        """

        logger.info("开始技能升级和转世操作")
        logger.debug("点击技能升级按钮")
        if self.shenji_times < 8:
            self.km.move_and_click(878, 991)
            # "", "", "3W敌法", "再生之力", "", "琉璃大炮", "",
            # "", "生命膨胀", "攻击强化",, "召唤", , "血之箭",
            # "浸毒武器", "小小之心", "剧毒体质", "多重射击", "毒液外衣",
            #
            # "极速箭术", "月神箭", "生命膨胀", "召唤", "血之箭", "琉璃大炮", "小金库", "百步穿杨"
            texts_to_find = ["极速箭术", "月神箭", "生命膨胀", "血之箭",
                             "琉璃大炮", "小金库", "百步穿杨","献祭",
                             "多重射击","浸毒武器","剧毒体质","死亡之舞","黄金剑",
                             "自愈之力"]  # 替换为实际需要检测的文本内容

            x, y, conf = self.vision.find_text("刷新", 775,758, 1095,855)  # 根据实际区域调整坐标范围
            if x > 0:
                self.shenji_times += 1
                for text in texts_to_find:
                    x, y, conf = self.vision.find_text(text, 512,442,1398,525)  # 根据实际区域调整坐标范围
                    if x > 0:
                        logger.info(f"找到文本 '{text}'，准备点击")
                        self.km.move_and_click(x, y)
                        break
                else:
                    self.km.move_and_click(770, 551,3)

        self.km.press_key("f1",2,0.1)
        self.km.press_key('a')
        self.km.move_and_click(963, 525)
        logger.debug("执行转世操作")
        self.km.move_and_click(947, 982)
        self.km.move_and_click(1034, 978)
        logger.debug("执行转世操作")
        self.km.move_and_click(770, 551, 3)
        self.km.move_and_click(1066, 634, 3)
        logger.info("技能升级和转世操作完成")