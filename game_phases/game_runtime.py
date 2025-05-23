# game_phases/game_runtime.py
import time
from loguru import logger
from game_components.item_manager import ItemManager


class PositionConstants:

    # 关闭商店
    CLOSE_STORE = (1664, 1045)
    # 投资按钮
    INVEST_TOGGLE = (806, 976)
    # 技能购买按钮
    SKILL_UPGRADE_BUTTON = (878, 991)
    # 默认技能位置
    DEFAULT_SKILL_POSITION = (770, 551)
    # 挑战升级按钮
    UPGRADE_CHALLENGE_LEVEL = (1872, 341)


    # 查找可选技能查找范围
    FIND_OPTIONAL_SKILL = (512, 442, 1398, 525)
    # 商店状态查找范围
    UPGRADE_TEXT_AREA = (1530, 12, 1896, 55)
    # 刷新按钮查找范围
    REFRESH_BOTTON = (813, 783, 1107, 867)


    # 转换耕作队列
    REBIRTH_SEQUENCE = [(947, 982), (1034, 978), (770, 551), (1066, 634)]
    # 移动到塔下操作列表
    TOWER_MOVE_REGION = (73, 911, 707, 420)




class InvestmentManager:
    def __init__(self, km, config):
        self.km = km
        self.config = config

    def toggle_investment(self):
        if not self.config.get("use_gold", True):
            return
        logger.info("[投资] 切换投资状态")
        self.km.right_click(*PositionConstants.INVEST_TOGGLE)
        self.km.return_to_initial_position()


class SkillUpgradeManager:
    def __init__(self, km, vision, config):
        self.km = km
        self.vision = vision
        self.config = config
        self.shenji_times = 0
        self.texts_to_find = [
            "极速箭术", "月神箭", "暴击强化", "生命膨胀", "血之箭",
            "琉璃大炮", "小金库", "百步穿杨", "献祭", "多重射击",
            "浸毒武器", "剧毒体质", "死亡之舞", "黄金剑", "自愈之力"
        ]

    def handle_skill_upgrades(self):
        if self.shenji_times >= 8:
            return

        self.km.move_and_click(*PositionConstants.SKILL_UPGRADE_BUTTON)

        time.sleep(1)
        x, y, conf = self.vision.find_text("刷新", *PositionConstants.REFRESH_BOTTON, save=True)
        if x > 0:
            self.shenji_times += 1
            logger.info(f"[技能升级] 第 {self.shenji_times} 次刷新")
            self.km.move_and_click(*self._get_shenji_position(), 1)

        self.km.return_to_initial_position()
        logger.debug("[技能升级] 执行转世操作")
        for pos in PositionConstants.REBIRTH_SEQUENCE:
            time.sleep(0.5)
            self.km.move_and_click(*pos)
        logger.info("[技能升级] 升级和转世完成")
    def _get_shenji_position(self):
        shenji_list = self.vision.get_all_coordinates_and_text(
            *PositionConstants.FIND_OPTIONAL_SKILL)

        for shenji_name in self.texts_to_find:
            for shenji_corr in shenji_list:
                if shenji_corr[2] == shenji_name:
                    return shenji_corr[0], shenji_corr[1]
        return PositionConstants.DEFAULT_SKILL_POSITION
class StoreManager:
    def __init__(self, km, vision):
        self.km = km
        self.vision = vision

    def open_store(self):
        for _ in range(5):  # 最多尝试5次
            x, y, _ = self.vision.find_text('升级物品', *PositionConstants.UPGRADE_TEXT_AREA)
            if x > 0:  # 如果找到"升级物品"，点击并退出
                self.km.move_and_click(x, y, 2)
                break
            # 没找到就尝试关闭商店
            self.km.move_and_click(*PositionConstants.CLOSE_STORE)
            time.sleep(1)

    def close_store(self):
        for _ in range(5):
            if self.vision.find_text('升级物品', *PositionConstants.UPGRADE_TEXT_AREA)[0] <= 0:
                break  # 如果条件不满足，提前退出循环
            self.km.move_and_click(*PositionConstants.CLOSE_STORE)
            time.sleep(1)

    def switch_store(self):
        self.open_store()
        self.km.right_click(1794, 343)
        self.km.right_click(1794, 343)
        self.close_store()


class CollapsePhase:
    def __init__(self, state_manager, km, vision, config):
        self.state_manager = state_manager
        self.km = km
        self.vision = vision
        self.config = config

        self.invest_mgr = InvestmentManager(km, config)
        self.skill_mgr = SkillUpgradeManager(km, vision, config)
        self.store_mgr = StoreManager(km, vision)
        self.item_mgr = ItemManager(state_manager, km, vision)
        logger.info("游戏阶段控制器初始化完成 | 投资管理、技能升级、商店管理、物品管理已加载")

    def execute(self):
        self.state_manager.wait_until_resumed()
        logger.info("=== 开始资源收集阶段 ===")

        investment_toggled = True
        taxia_performed = False
        FIND_TEXT_TIMEOUT = 60
        games_success = True

        while True:
            _, exec_time_sec = self.vision.get_run_time()
            logger.info(f"当前游戏运行时间: {exec_time_sec // 60}分{exec_time_sec % 60}秒")

            # 投资管理
            if exec_time_sec < 60 and investment_toggled:
                logger.info("执行初始投资切换...")
                self.invest_mgr.toggle_investment()
                investment_toggled = False

            # 商店管理
            self.store_mgr.close_store()

            # 检测结束条件
            x, y, conf = self.vision.find_text("收起", 700, 706, 1145, 925)
            if x > 0:
                logger.success(f"检测到结束条件 | 点击收起按钮 ({x}, {y})")
                games_success = self.vision.find_text("失败", 645,170,1484,296  )[0] <= 0
                self.km.move_and_click(x, y, 2)
                time.sleep(1)
                break

            self.km.return_to_initial_position()

            # 超时重新投资
            if not investment_toggled and exec_time_sec > FIND_TEXT_TIMEOUT:
                logger.info("达到超时时间，重新切换投资状态")
                self.invest_mgr.toggle_investment()
                investment_toggled = True

            # 特殊阶段操作
            if not taxia_performed and exec_time_sec > 1000:
                logger.info(">>> 进入特殊阶段操作 <<<")
                logger.info("商店切换操作...")
                self.store_mgr.switch_store()
                logger.info("执行塔下特殊操作...")
                self._perform_special_operations()
                self.skill_mgr.shenji_times = 0
                taxia_performed = True
                logger.info("<<< 特殊阶段操作完成 >>>")

            # 常规操作循环
            if exec_time_sec < 1000:
                if self.config.get("useMoney", True):
                    logger.info("处理技能升级...")
                    self.skill_mgr.handle_skill_upgrades()

                logger.info("挑战等级升级...")
                self.km.move_and_click(*PositionConstants.UPGRADE_CHALLENGE_LEVEL, 5)

                logger.info("使用存储物品...")
                self.item_mgr.use_items()

                time.sleep(5)

        logger.success(f"资源收集阶段完成 | 总耗时: {exec_time_sec // 60}分{exec_time_sec % 60}秒")
        return games_success

    def _perform_special_operations(self):
        logger.info("移动到塔区域...")
        self.km.move_to_position(*PositionConstants.TOWER_MOVE_REGION)
        logger.info("等待30秒特殊操作时间...")
        time.sleep(30)
        self.km.return_to_initial_position()