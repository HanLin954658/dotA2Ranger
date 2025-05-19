import ctypes
import time
from loguru import logger
import math
import random
from ctypes import wintypes

from utils.state_manager import StateManager

# Windows API 常量和结构定义
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_ABSOLUTE = 0x8000

KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002

# 键盘虚拟键码常量
VK_F1 = 0x70
VK_A = 0x41
VK_D = 0x44


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_short),
        ("wParamH", ctypes.c_ushort)
    ]


class INPUT_union(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT)
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("union", INPUT_union)
    ]


class KMController:
    """键盘鼠标操作控制器，使用ctypes直接调用Windows API"""

    def __init__(self):
        logger.info("初始化键鼠控制器(ctypes版)")
        self.state_mgr = StateManager()
        logger.debug(f"状态管理器已注入: {type(self.state_mgr).__name__}")

        # 获取屏幕分辨率
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)
        logger.info(f"检测到屏幕分辨率: {self.screen_width}x{self.screen_height}")

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
            self._mouse_move(x, y)
            time.sleep(0.05)
            for _ in range(clicks):
                self._mouse_click(x, y)
                time.sleep(interval)
            time.sleep(0.5)
            logger.success(f"点击操作成功: ({x}, {y},  {clicks}次, 间隔{interval}s)")
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

        # 转换按键名称为虚拟键码
        key_code = self._get_virtual_key_code(key)

        try:
            for i in range(presses):
                self._key_press(key_code)
                time.sleep(interval)
            time.sleep(0.5)
            logger.success(f"按键 {key} {presses} 次完成")
        except Exception as e:
            logger.error(f"按键操作异常: {str(e)}")
            raise

    def move_to_position(self, sm_x: int, sm_y: int, bg_x: int, bg_y: int) -> None:
        """
        游戏地图坐标转换操作
        参数: sm_x, sm_y - 小地图坐标; bg_x, bg_y - 大地图坐标
        """
        logger.debug(f"开始地图跳转: 小图({sm_x}, {sm_y}) → 主图({bg_x}, {bg_y})")
        self.state_mgr.wait_until_resumed()

        try:
            self.move_and_click(sm_x, sm_y, 2, 1)
            time.sleep(1)
            self.move_and_click(bg_x, bg_y, 1, 1)
            self.press_key('f1', 1, 0.1)
            self.press_key('a')
            self.move_and_click(bg_x, bg_y, 1, 1)
            time.sleep(1)
            self.press_key('d', 5, interval=1)
            logger.success(f"地图跳转成功,坐标：({sm_x},{sm_y}), ({bg_x},{bg_y}))")
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

        try:
            self._mouse_move(x, y)
            self._mouse_right_click(x, y)
            logger.success(f"右键点击 ({x}, {y}) 成功")
        except Exception as e:
            logger.error(f"右键点击异常: {str(e)}")
            raise
    def _mouse_move(self, x: int, y: int) -> None:
        """移动鼠标到指定坐标"""
        # 将屏幕坐标转换为Windows API所需的相对坐标
        x = int((x / self.screen_width) * 65535)
        y = int((y / self.screen_height) * 65535)

        input_move = INPUT(type=INPUT_MOUSE)
        input_move.union.mi.dx = x
        input_move.union.mi.dy = y
        input_move.union.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE

        user32.SendInput(1, ctypes.byref(input_move), ctypes.sizeof(INPUT))

    def _mouse_click(self, x: int, y: int) -> None:
        """点击鼠标左键"""
        # 先移动到指定位置
        self._mouse_move(x, y)
        time.sleep(0.01)

        # 按下左键
        input_down = INPUT(type=INPUT_MOUSE)
        input_down.union.mi.dwFlags = MOUSEEVENTF_LEFTDOWN

        # 释放左键
        input_up = INPUT(type=INPUT_MOUSE)
        input_up.union.mi.dwFlags = MOUSEEVENTF_LEFTUP

        # 发送点击事件
        user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(INPUT))
        time.sleep(0.02)  # 模拟真实点击延迟
        user32.SendInput(1, ctypes.byref(input_up), ctypes.sizeof(INPUT))

    def _mouse_right_click(self, x: int, y: int) -> None:
        """点击鼠标右键"""
        # 先移动到指定位置
        self._mouse_move(x, y)
        time.sleep(0.01)

        # 按下右键
        input_down = INPUT(type=INPUT_MOUSE)
        input_down.union.mi.dwFlags = MOUSEEVENTF_RIGHTDOWN

        # 释放右键
        input_up = INPUT(type=INPUT_MOUSE)
        input_up.union.mi.dwFlags = MOUSEEVENTF_RIGHTUP

        # 发送点击事件
        user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(INPUT))
        time.sleep(0.02)  # 模拟真实点击延迟
        user32.SendInput(1, ctypes.byref(input_up), ctypes.sizeof(INPUT))

    def _key_press(self, key_code: int) -> None:
        """按下并释放指定按键"""
        extra = ctypes.c_ulong(0)
        ii_keydown = KEYBDINPUT(key_code, 0, 0, 0, ctypes.pointer(extra))
        ii_keyup = KEYBDINPUT(key_code, 0, KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))

        x = INPUT(type=INPUT_KEYBOARD, union=INPUT_union(ki=ii_keydown))
        y = INPUT(type=INPUT_KEYBOARD, union=INPUT_union(ki=ii_keyup))

        # 按下按键
        user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(INPUT))
        time.sleep(0.02)  # 按键持续时间
        # 释放按键
        user32.SendInput(1, ctypes.byref(y), ctypes.sizeof(INPUT))

    def _get_mouse_position(self) -> tuple:
        """获取当前鼠标位置"""

        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y

    def _get_virtual_key_code(self, key: str) -> int:
        """将按键名称转换为虚拟键码"""
        key_mapping = {
            'f1': VK_F1,
            'a': VK_A,
            'd': VK_D,
            # 可扩展更多按键映射...
        }

        return key_mapping.get(key.lower(), 0)

    def _generate_bezier_points(self, start_x, start_y, end_x, end_y, num_points=20):
        """生成贝塞尔曲线路径点，使鼠标移动更自然"""
        # 计算控制点（随机偏移以模拟人类移动）
        control_x1 = start_x + (end_x - start_x) * 0.3 + (random.random() - 0.5) * 50
        control_y1 = start_y + (end_y - start_y) * 0.3 + (random.random() - 0.5) * 50
        control_x2 = start_x + (end_x - start_x) * 0.7 + (random.random() - 0.5) * 50
        control_y2 = start_y + (end_y - start_y) * 0.7 + (random.random() - 0.5) * 50

        # 生成贝塞尔曲线上的点
        points = []
        for i in range(num_points + 1):
            t = i / num_points
            x = (1 - t) ** 3 * start_x + 3 * (1 - t) ** 2 * t * control_x1 + 3 * (
                        1 - t) * t ** 2 * control_x2 + t ** 3 * end_x
            y = (1 - t) ** 3 * start_y + 3 * (1 - t) ** 2 * t * control_y1 + 3 * (
                        1 - t) * t ** 2 * control_y2 + t ** 3 * end_y
            points.append((int(x), int(y)))

        return points