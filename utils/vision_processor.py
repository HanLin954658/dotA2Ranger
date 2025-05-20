import time

from paddleocr import PaddleOCR
import numpy as np
from PIL import ImageGrab,Image
import cv2
from loguru import logger


class SingletonMeta(type):
    """
    单例模式的元类
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class VisionProcess(metaclass=SingletonMeta):
    def __init__(self):
        # 初始化OCR引擎
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch")
        logger.info("OCR引擎初始化完成")

    def find_text(self, text, x1, y1, x2, y2, threshold=0.6):
        """
        在指定区域内查找文本
        :param text: 要查找的文本
        :param x1: 区域左上角的 x 坐标
        :param y1: 区域左上角的 y 坐标
        :param x2: 区域右下角的 x 坐标
        :param y2: 区域右下角的 y 坐标
        :param threshold: 匹配阈值，范围从 0 到 1
        :return: 匹配文本的中心坐标 (x, y) 和置信度，如果未找到则返回 (-1, -1, 0)
        """
        logger.debug(f"开始在区域 ({x1}, {y1}, {x2}, {y2}) 内查找文本: {text}")
        time.sleep(0.5)
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        result = self.ocr.ocr(np.array(screenshot), cls=True)
        if result[0] is None:
            logger.info(f"未找到文本 {text}")
            return -1, -1, 0

        for line in result:
            for box in line:
                detected_text = box[1][0]
                confidence = box[1][1]
                if text in detected_text:# and confidence >= threshold:
                    # 计算文本中心坐标
                    coords = box[0]
                    center_x = (coords[0][0] + coords[1][0] + coords[2][0] + coords[3][0]) / 4 + x1
                    center_y = (coords[0][1] + coords[1][1] + coords[2][1] + coords[3][1]) / 4 + y1
                    logger.info(f"找到文本 {text}，中心坐标: ({center_x}, {center_y})，置信度: {confidence}")
                    return center_x, center_y, confidence
        logger.info(f"未找到符合条件的文本 {text}")
        return -1, -1, 0

    def find_image(self, template_path, x1, y1, x2, y2, threshold=0.8):
        """
        在指定区域内查找图像并返回中心坐标
        :param template_path: 模板图像的文件路径
        :param x1: 区域左上角的 x 坐标
        :param y1: 区域左上角的 y 坐标
        :param x2: 区域右下角的 x 坐标
        :param y2: 区域右下角的 y 坐标
        :param threshold: 匹配阈值，范围从 0 到 1
        :return: 匹配图像的中心坐标 (x, y)，如果未找到则返回 (-1, -1)
        """
        logger.debug(f"开始在区域 ({x1}, {y1}, {x2}, {y2}) 内查找图像: {template_path}")
        # 截取指定区域的屏幕截图
        time.sleep(0.5)
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # 读取模板图像
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)

        # 进行模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            h, w, _ = template.shape
            center_x = max_loc[0] + w // 2 + x1
            center_y = max_loc[1] + h // 2 + y1
            logger.info(f"找到图像 {template_path}，中心坐标: ({center_x}, {center_y})")
            return center_x, center_y
        else:
            logger.info(f"未找到图像 {template_path}")
            return -1, -1

    def get_run_time(self,x1=897,y1=0,x2=1015,y2=27, scale=2):
        """
        将输入的NumPy数组图像扩大，并用黑色填充边缘
        :param x1: 区域左上角的 x 坐标
        :param y1: 区域左上角的 y 坐标
        :param x2: 区域右下角的 x 坐标
        :param y2: 区域右下角的 y 坐标
        :param scale: 扩大倍数（默认2倍）
        :return: 扩大后的图像（NumPy数组）
        """
        # 1. 将NumPy数组转为PIL图像
        try:
            time.sleep(0.5)
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))

            # 2. 原始尺寸
            original_width, original_height = img.size

            # 3. 新尺寸
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)

            # 4. 创建黑色背景的新图像
            expanded_img = Image.new("RGB", (new_width, new_height), (0, 0, 0))

            # 5. 计算居中位置并粘贴
            paste_x = (new_width - original_width) // 2
            paste_y = (new_height - original_height) // 2
            expanded_img.paste(img, (paste_x, paste_y))
            result = self.ocr.ocr(np.array(expanded_img), cls=True)
            if result[0] is None or (":" not in result[0][0][1][0]):
                logger.info(f"未找到当前运行时间")
                return 0, 60
            minutes, seconds = map(int, result[0][0][1][0].split(':'))
            return result[0][0][1][0], minutes * 60 + seconds
        except Exception as e:
            logger.error(f"Error in get_current_time: {e}\n,{result}")
            return 0, 60

