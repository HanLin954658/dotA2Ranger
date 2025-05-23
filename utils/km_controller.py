import ctypes
import time
from loguru import logger


from utils.state_manager import StateManager

# Windows API 常量和结构定义
user32 = ctypes.windll.user32

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_WHEEL = 0x0800

KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002


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

        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)
        logger.info(f"检测到屏幕分辨率: {self.screen_width}x{self.screen_height}")

    def move_and_click(self, x: int, y: int, clicks: int = 1, interval: float = 0.2) -> None:
        logger.debug(f"准备移动到 ({x}, {y}) 点击 {clicks} 次")
        self.state_mgr.wait_until_resumed()

        if not (0 <= x <= self.screen_width and 0 <= y <= self.screen_height):
            logger.warning(f"无效坐标: ({x}, {y})")
            return

        try:
            self._mouse_move(x, y)
            time.sleep(0.05)
            for _ in range(clicks):
                self._mouse_click(x, y)
                time.sleep(interval)
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"点击操作异常: {str(e)}")
            raise
    def return_to_initial_position(self):
        self.move_a_to_target_position(93,935,884,457)

    def move_a_to_target_position(self,  x1: int, y1: int, x2: int, y2: int):
        self.press_key('f1',3)
        if x1 !=0:
            self.move_and_click(x1, y1)
        self.press_key('a')
        self.move_and_click(x2, y2)


    def right_click(self, x: int, y: int, wait: float = 0) -> None:
        logger.debug(f"准备右键点击 ({x}, {y})")
        self.state_mgr.wait_until_resumed()

        try:
            self._mouse_move(x, y)
            self._mouse_right_click(x, y)
            time.sleep(wait)
        except Exception as e:
            logger.error(f"右键点击异常: {str(e)}")
            raise

    def press_key(self, key: str, presses: int = 1, interval: float = 0.5) -> None:
        logger.debug(f"准备按键 {key} {presses} 次")
        self.state_mgr.wait_until_resumed()

        key_code = self._get_virtual_key_code(key.lower())

        try:
            for _ in range(presses):
                self._key_press(key_code)
                time.sleep(interval)
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"按键操作异常: {str(e)}")
            raise

    def move_to_position(self, sm_x: int, sm_y: int, bg_x: int, bg_y: int) -> None:
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
        except Exception as e:
            logger.error(f"地图跳转失败: {str(e)}")
            raise

    def mouse_drag(self,x1,y1,x2,y2):
        self._mouse_move(x1,y1)
        self._mouse_down()
        self._mouse_move(x2,y2)
        self._mouse_up()


    def _mouse_move(self, x: int, y: int) -> None:
        x = int((x / self.screen_width) * 65535)
        y = int((y / self.screen_height) * 65535)

        input_move = INPUT(type=INPUT_MOUSE)
        input_move.union.mi.dx = x
        input_move.union.mi.dy = y
        input_move.union.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE

        self._send_input(input_move)

    def mouse_scroll(self,scroll_amount: int):
        input_struct = INPUT(type=INPUT_MOUSE)
        input_struct.union.mi.dwFlags = MOUSEEVENTF_WHEEL
        input_struct.union.mi.mouseData = scroll_amount * 120  # WHEEL_DELTA=120是标准值

        # 发送输入
        self._send_input(input_struct)

        time.sleep(0.05)
    def _mouse_right_click(self, x: int, y: int) -> None:
        self._mouse_move(x, y)
        time.sleep(0.01)

        input_down = INPUT(type=INPUT_MOUSE)
        input_down.union.mi.dwFlags = MOUSEEVENTF_RIGHTDOWN
        input_up = INPUT(type=INPUT_MOUSE)
        input_up.union.mi.dwFlags = MOUSEEVENTF_RIGHTUP

        self._send_input(input_down)
        time.sleep(0.02)
        self._send_input(input_up)

    def _key_press(self, key_code: int) -> None:
        extra = ctypes.c_ulong(0)
        ii_keydown = KEYBDINPUT(key_code, 0, 0, 0, ctypes.pointer(extra))
        ii_keyup = KEYBDINPUT(key_code, 0, KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))

        self._send_input(INPUT(type=INPUT_KEYBOARD, union=INPUT_union(ki=ii_keydown)))
        time.sleep(0.02)
        self._send_input(INPUT(type=INPUT_KEYBOARD, union=INPUT_union(ki=ii_keyup)))

    def _send_input(self, input_obj: INPUT) -> None:
        user32.SendInput(1, ctypes.byref(input_obj), ctypes.sizeof(INPUT))
    def _mouse_down(self) -> None:
        """模拟鼠标按下动作"""
        input_down = INPUT(type=INPUT_MOUSE)
        input_down.union.mi.dwFlags = MOUSEEVENTF_LEFTDOWN
        self._send_input(input_down)
        time.sleep(0.02)

    def _mouse_up(self) -> None:
        """模拟鼠标弹起动作"""
        input_up = INPUT(type=INPUT_MOUSE)
        input_up.union.mi.dwFlags = MOUSEEVENTF_LEFTUP
        self._send_input(input_up)

    def _mouse_click(self, x: int, y: int) -> None:
        """完整的鼠标点击操作（移动+按下+弹起）"""
        self._mouse_move(x, y)
        self._mouse_down()
        self._mouse_up()
    def _get_virtual_key_code(self, key: str) -> int:
        key_mapping = {
            # 字母
            'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
            'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
            'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
            'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
            'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,

            # 数字
            '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
            '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,

            # 功能键
            'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74,
            'f6': 0x75, 'f7': 0x76, 'f8': 0x77, 'f9': 0x78, 'f10': 0x79,
            'f11': 0x7A, 'f12': 0x7B,

            # 控制键
            'ctrl': 0x11, 'shift': 0x10, 'alt': 0x12,
            'enter': 0x0D, 'esc': 0x1B, 'tab': 0x09, 'space': 0x20,
            'backspace': 0x08,

            # 方向键
            'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,

            # 其他键
            'insert': 0x2D, 'delete': 0x2E, 'home': 0x24, 'end': 0x23,
            'pageup': 0x21, 'pagedown': 0x22, 'capslock': 0x14,
            'numlock': 0x90, 'scrolllock': 0x91, 'pause': 0x13,
            'printscreen': 0x2C,
        }

        code = key_mapping.get(key)
        if code is None:
            logger.error(f"无法识别按键: {key}")
            raise ValueError(f"未定义的按键映射: {key}")
        return code
