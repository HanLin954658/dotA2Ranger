"""
游戏自动化系统
主模块，负责协调游戏自动化任务的执行流程
"""
import os
import time
from loguru import logger
from typing import Dict, Any, Optional

# 配置和工具
from config.config_loader import load_config
from utils.state_manager import StateManager
from utils.keyboard_listener import KeyboardListener
from utils.km_controller import KMController

# 游戏自动化组件
from game_components.game_phases import GamePhaseManager
from utils.vision_processor import VisionProcess
from gui.user_settings_gui import get_user_settings

# 设置日志
def setup_logging():
    """配置日志系统，设置日志文件路径和格式"""
    logger.info("初始化日志系统")
    log_dir = os.path.join(os.path.dirname(__file__), '../logs')
    os.makedirs(log_dir, exist_ok=True)
    logger.debug(f"日志目录: {log_dir}")

    logger.add(
        os.path.join(log_dir, 'game_automation.log'),
        level='INFO',
        format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {function}:{line} - {message}',
        encoding='utf-8',
        rotation='100 MB',
        retention='7 days'
    )
    logger.info("日志系统配置完成")


class GameAutomation:
    """
    游戏自动化主类，负责协调和控制整个游戏自动化流程
    管理核心组件初始化、主循环执行和资源清理
    """

    def __init__(self):
        """初始化游戏自动化系统，加载配置并初始化各组件"""
        logger.info("===== 游戏自动化系统初始化 =====")
        setup_logging()
        logger.info("正在初始化游戏自动化系统...")

        # 初始化核心组件
        logger.debug("初始化状态管理器")
        self.state_manager = StateManager()

        logger.debug("初始化键盘鼠标控制器")
        self.km_controller = KMController()

        logger.debug("初始化视觉处理器")
        self.detection_service = VisionProcess()

        # 加载配置
        logger.debug("加载配置文件")
        self.config = get_user_settings()
        self._log_config()

        # 初始化游戏阶段管理器
        logger.debug("初始化游戏阶段管理器")
        self.phase_manager = GamePhaseManager(
            self.state_manager,
            self.km_controller,
            self.detection_service,
            self.config
        )

        # 初始化键盘监听器用于控制
        logger.debug("初始化键盘监听器")
        self.keyboard_listener = KeyboardListener(self.state_manager.toggle_pause)
        logger.info("启动键盘监听线程")
        self.keyboard_listener.start()

        # 状态跟踪
        self.is_first_start = True
        logger.info("游戏自动化系统初始化完成")

    def _log_config(self):
        """记录当前加载的配置信息"""
        logger.info("===== 当前配置 =====")
        logger.info(f"配置内容: {self.config}")
        logger.info(f"起始阶段: {self.config.get('Var1', '难度')}")
        logger.info(f"难度级别: {self.config.get('nandu', 10) - 1}")
        logger.info(f"使用资源: {self.config.get('useMoney', True)}")
        logger.info("===== 配置结束 =====")

    def main_loop(self):
        """自动化系统的主执行循环，控制游戏各阶段的执行顺序"""
        logger.info("等待用户启动自动化流程...")
        self.state_manager.wait_until_resumed()
        logger.info("脚本已启动。按F11暂停/恢复。")

        while True:
            # 从配置获取当前阶段或继续执行序列
            starting_phase = self.config.get("Var1", "收起")
            logger.debug(f"当前配置的起始阶段: {starting_phase}")

            # 按顺序执行各阶段
            if not self.is_first_start or starting_phase == "开局":
                logger.info("========主流程：开始执行游戏启动阶段=======")
                if self.is_first_start:
                    logger.info("========主流程：首次启动序列执行完毕=======")
                    self.is_first_start = False
                self.phase_manager.handle_game_start()
                logger.info("游戏启动阶段完成")

            if not self.is_first_start or starting_phase == "收起":
                logger.info("========主流程：开始执行资源收集阶段=======")
                if self.is_first_start:
                    logger.info("========主流程：首次启动序列执行完毕=======")
                    self.is_first_start = False
                self.phase_manager.handle_collapse()
                logger.info("资源收集阶段完成")

            if not self.is_first_start or starting_phase == "重开":
                logger.info("========主流程：开始执行游戏重开阶段=======")
                if self.is_first_start:
                    logger.info("========主流程：首次启动序列执行完毕=======")
                    self.is_first_start = False
                self.phase_manager.handle_restart()
                logger.info("游戏重开阶段完成")

            if not self.is_first_start or starting_phase == "难度":
                logger.info("========主流程：开始执行难度选择阶段=======")
                if self.is_first_start:
                    logger.info("========主流程：首次启动序列执行完毕=======")
                    self.is_first_start = False
                self.phase_manager.handle_difficulty()
                logger.info("难度选择阶段完成")

            # 标记首次启动已完成


            # 防止CPU占用过高
            time.sleep(0.1)

    def cleanup(self):
        """在程序退出前清理资源，确保所有线程和连接正常关闭"""
        logger.info("===== 资源清理开始 =====")

        logger.info("停止键盘监听线程")
        self.keyboard_listener.stop()

        logger.info("释放其他资源...")
        # 可以添加更多清理操作

        logger.info("===== 资源清理完成 =====")