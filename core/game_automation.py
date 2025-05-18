import os
import time
import pyautogui
from loguru import logger
from config.config_loader import load_config
from utils.state_manager import StateManager
from utils.image_finder import ImageFinder
from utils.ocr_handler import OCRHandler
from utils.mouse_controller import MouseController
from utils.keyboard_listener import KeyboardListener
from utils.screenshot_handler import ScreenshotHandler

# 确保日志目录存在
LOG_DIR = os.path.join(os.path.dirname(__file__), '../logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志
logger.add(
    os.path.join(LOG_DIR, 'test.log'),
    level='INFO',
    format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {function}:{line} - {message}',
    encoding='utf-8',
    rotation='100 MB',
    retention='7 days'
)

class GameAutomation:
    def __init__(self):
        # 初始化OCR引擎
        self.ocr_handler = OCRHandler()

        # 从配置获取用户设置
        config = load_config()
        self.Var1 = config.get("Var1", "收起")
        self.nandu = config.get("nandu", 6) - 1
        self.useMoney = config.get("useMoney", True)
        print("Var1:", self.Var1)
        print("nandu:", self.nandu)
        print("useMoney:", self.useMoney)
        # 脚本状态控制
        self.paused = False
        self.is_first_start = True

        # 初始化状态管理器
        self.state_manager = StateManager()

        # 初始化键盘监听器
        self.keyboard_listener = KeyboardListener(self.state_manager.toggle_pause)
        self.keyboard_listener.start()

        # 初始化鼠标控制器
        self.mouse_controller = MouseController()

        # 初始化截图处理器
        self.screenshot_handler = ScreenshotHandler()

        # 初始化找图处理器
        self.image_finder = ImageFinder()

    def use_items(self):
        """使用道具函数"""
        self.state_manager.wait_until_resumed()
        logger.info("开始使用道具")
        while True:
            # 升级
            x, y = self.image_finder.find_image_in_area("images/shengji.bmp", 1142, 931, 1372, 1064)
            if x > 0:
                self.mouse_controller.move_and_click(x, y)
                # 查找攻速
                x11, y11, conf11 = self.ocr_handler.find_text_in_area("攻击速度", 803, 335, 1075, 591)
                if x11 > 0:
                    logger.info("找到攻速")
                    self.mouse_controller.move_and_click(x11, y11, 2)
                    continue
                # 点击默认位置
                self.mouse_controller.move_and_click(898, 561, 2)
                continue

            # 神话
            x, y = self.image_finder.find_image_in_area("images/shenhua.bmp", 1142, 931, 1372, 1064)
            if x > 0:
                self.mouse_controller.move_and_click(x, y)
                self.mouse_controller.move_and_click(898, 561, 2)
                continue

            # 全能
            x, y = self.image_finder.find_image_in_area("images/quanneng.bmp", 1142, 931, 1372, 1064)
            if x > 0:
                self.mouse_controller.move_and_click(x, y)
                continue

            # 抉择
            x, y = self.image_finder.find_image_in_area("images/jueze.bmp", 1142, 931, 1372, 1064)
            if x > 0:
                self.mouse_controller.move_and_click(x, y)
                self.mouse_controller.move_and_click(898, 561, 2)
                continue

            # 全部完成
            break

    def investment_toggle(self):
        """投资启停函数"""
        self.state_manager.wait_until_resumed()
        if not self.useMoney:
            logger.info("未开启金币消耗")
            return

        logger.info("投资启停")
        pyautogui.moveTo(806, 976, duration=0.2)
        pyautogui.rightClick()
        time.sleep(1)

    def skill_and_reincarnation(self):
        """神技和转生函数"""
        self.state_manager.wait_until_resumed()
        if not self.useMoney:
            logger.info("未开启金币消耗")
            return

        logger.info("升级神技&转生")
        self.mouse_controller.move_and_click(878, 991)
        self.mouse_controller.move_and_click(952, 981)
        self.mouse_controller.move_and_click(1024, 977)
        time.sleep(1)
        self.mouse_controller.move_and_click(770, 551, 3)
        self.mouse_controller.move_and_click(1066, 634, 3)

    def move_to_position(self, small_map_x, small_map_y, big_map_x, big_map_y):
        """移动到指定位置"""
        self.mouse_controller.move_and_click(small_map_x, small_map_y)
        pyautogui.moveTo(big_map_x, big_map_y)
        # 模拟按D键
        for _ in range(5):
            self.mouse_controller.press_key('d')

    def handle_start_game(self):
        """处理开局流程"""
        self.state_manager.wait_until_resumed()
        logger.info("执行开局流程")
        self.is_first_start = False
        while True:
            x, y, conf = self.ocr_handler.find_text_in_area("普通模式", 1063, 6, 1171, 36)
            if x > 0:
                time.sleep(5)
                self.move_to_position(93, 928, 886, 495)
                break
            time.sleep(3)

    def handle_collapse(self):
        """处理收起流程"""
        self.state_manager.wait_until_resumed()
        logger.info("执行收起流程")
        self.is_first_start = False
        start_time = time.time()
        self.investment_toggle()

        # 状态标记
        investment_toggled = False
        taxia_performed = False

        # 超时设置
        FIND_TEXT_TIMEOUT = 180  # 查找"收起"按钮的超时时间

        while True:
            # 计算已执行时间
            elapsed_time = time.time() - start_time
            # 查找"收起"按钮
            x, y, conf = self.ocr_handler.find_text_in_area("收起", 700, 706, 1145, 925)
            self.mouse_controller.press_key('f1', 3)  # 可能是刷新界面的操作？

            if x > 0:
                logger.info(f"找到'收起'按钮，坐标: ({x}, {y})，准备点击")
                self.mouse_controller.move_and_click(x, y, 2)
                time.sleep(1)  # 点击后等待一下，确保操作完成
                break
            # 查找"收起"按钮并点击
            if not investment_toggled and elapsed_time > FIND_TEXT_TIMEOUT:
                logger.info(f"已执行 {elapsed_time:.2f} 秒，切换投资状态")
                self.investment_toggle()
                investment_toggled = True

            # 执行taxia操作
            if not taxia_performed and elapsed_time > 900:
                logger.info(f"已执行 {elapsed_time:.2f} 秒，准备执行taxia操作")
                self.move_to_position(77, 918, 545, 219)
                time.sleep(15)
                self.mouse_controller.press_key('f2', 3)
                taxia_performed = True

            # 在特定时间范围内使用物品
            if elapsed_time < 900:  # 提前一点结束，避免与taxia操作冲突
                self.use_items()

            # 执行技能和轮回操作
            self.skill_and_reincarnation()

            # 循环间隔
            time.sleep(5)

        logger.info(f"收起流程执行完毕，总耗时 {time.time() - start_time:.2f} 秒")

    def handle_restart(self):
        """处理重开流程"""
        self.state_manager.wait_until_resumed()
        logger.info("执行重开流程")
        self.is_first_start = False
        self.mouse_controller.move_and_click(112, 955)
        time.sleep(1)

        while True:
            x, y, conf = self.ocr_handler.find_text_in_area("重开游戏", 809, 565, 905, 597)
            if x > 0:
                logger.info("开始重开")
                self.mouse_controller.move_and_click(x, y, 2)
                break
            time.sleep(5)

        time.sleep(1)
        self.mouse_controller.move_and_click(840, 622, 2)

    def handle_difficulty(self, nandu):
        """处理难度选择流程"""
        self.state_manager.wait_until_resumed()
        logger.info("执行难度选择流程")
        self.is_first_start = False
        while True:
            x, y, conf = self.ocr_handler.find_text_in_area("开始游戏", 1649, 939, 1819, 995)
            logger.info("选择难度")
            if x > 0:
                # 计算难度位置
                difficulty_y = 291 + nandu * 53
                self.mouse_controller.move_and_click(953, difficulty_y, 3)
                self.mouse_controller.move_and_click(x, y, 2)
                break
            time.sleep(5)

    def main_loop(self):
        """主循环"""
        self.state_manager.wait_until_resumed()
        logger.info("脚本已启动，按F11暂停/恢复")

        while True:
            if not self.is_first_start or self.Var1 == "开局":
                self.handle_start_game()
            if not self.is_first_start or self.Var1 == "收起":
                self.handle_collapse()
            if not self.is_first_start or self.Var1 == "重开":
                self.handle_restart()
            if not self.is_first_start or self.Var1 == "难度":
                self.handle_difficulty(self.nandu)

            # 防止CPU占用过高
            time.sleep(0.1)