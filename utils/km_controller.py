import pyautogui
import time
from loguru import logger

from utils.state_manager import StateManager


class KMController:
    """键盘鼠标操作控制器，集成状态检查和安全操作"""

    def __init__(self):
        logger.info("初始化键鼠控制器")
        self.state_mgr = StateManager()
        logger.debug(f"状态管理器已注入: {type(self.state_mgr).__name__}")

    def move_and_click(self, x: int, y: int, clicks: int = 1, interval: float = 0.2) -> None:
        """
        移动并点击目标坐标
        参数: x, y - 屏幕坐标; clicks - 点击次数; interval - 点击间隔
        """
        logger.debug(f"准备移动到 ({x}, {y}) 点击 {clicks} 次")
        self.state_mgr.wait_until_resumed()

        if x < 0 or y < 0:
            logger.warning(f"无效坐标: ({x}, {y})")
            return

        try:
            logger.info(f"开始移动鼠标到 ({x}, {y})")
            pyautogui.moveTo(x, y, duration=0.1)
            time.sleep(0.5)
            logger.debug(f"执行点击操作 {clicks} 次")
            pyautogui.click(clicks=clicks, interval=interval)
            logger.success(f"成功点击坐标: ({x}, {y}) 次数: {clicks}")
        except pyautogui.FailSafeException as e:
            logger.error(f"安全保护触发: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"点击操作异常: {str(e)}")
            raise

    def press_key(self, key: str, presses: int = 1, interval: float = 0.5) -> None:
        """
        模拟键盘按键
        参数: key - 按键名称; presses - 按键次数; interval - 按键间隔
        """
        logger.debug(f"准备按键 {key} {presses} 次")
        self.state_mgr.wait_until_resumed()

        try:
            for i in range(presses):
                logger.info(f"正在按下 {key} (第 {i + 1}/{presses} 次)")
                pyautogui.press(key)
                time.sleep(interval)
            logger.success(f"完成按键操作: {key}x{presses}")
        except Exception as e:
            logger.error(f"按键操作异常: {str(e)}")
            raise

    def move_to_position(self, sm_x: int, sm_y: int, bg_x: int, bg_y: int) -> None:
        """
        游戏地图坐标转换操作
        参数: sm_x, sm_y - 小地图坐标; bg_x, bg_y - 大地图坐标
        """
        logger.info(f"开始地图跳转: 小图({sm_x}, {sm_y}) → 主图({bg_x}, {bg_y})")
        self.state_mgr.wait_until_resumed()

        try:
            logger.debug("执行小地图点击")
            self.move_and_click(sm_x, sm_y,4,0.5)

            logger.debug("移动到大地图目标位置")
            pyautogui.moveTo(bg_x, bg_y, duration=0.1)
            logger.info("模拟角色移动操作")
            self.press_key('a')
            pyautogui.click(963, 525)
            self.press_key('d',5,interval=0.5)

            logger.success("地图跳转操作完成")
        except Exception as e:
            logger.error(f"地图跳转失败: {str(e)}")
            raise

    def right_click(self, x: int, y: int, wait: float = 0) -> None:
        """
        右键点击目标坐标
        参数: x, y - 屏幕坐标; wait - 操作后等待时间
        """
        logger.debug(f"准备右键点击 ({x}, {y})")
        self.state_mgr.wait_until_resumed()
        original_pos = pyautogui.position()
        logger.debug(f"原始光标位置: {original_pos}")

        try:
            logger.info(f"移动鼠标到 ({x}, {y})")
            pyautogui.moveTo(x, y, duration=0.2)

            logger.debug("执行右键点击")
            pyautogui.rightClick()
            logger.success(f"右键点击完成: ({x}, {y})")

            if wait > 0:
                logger.debug(f"等待 {wait} 秒")
                time.sleep(wait)
        except Exception as e:
            logger.error(f"右键点击异常: {str(e)}")
            raise
        finally:
            logger.debug("恢复光标原始位置")
            pyautogui.moveTo(original_pos)