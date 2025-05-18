from paddleocr import PaddleOCR
import numpy as np
from PIL import ImageGrab
from loguru import logger

class OCRHandler:
    def __init__(self):
        # 初始化OCR引擎
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch")

    def find_text_in_area(self, text, x1, y1, x2, y2, threshold=0.7):
        """在指定区域内查找文本"""
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        result = self.ocr.ocr(np.array(screenshot), cls=True)
        if result[0] is None:
            logger.info(f"未找到文本{text}")
            return -1, -1, 0

        for line in result:
            for box in line:
                detected_text = box[1][0]
                confidence = box[1][1]
                if text in detected_text and confidence >= threshold:
                    # 计算文本中心坐标
                    coords = box[0]
                    center_x = (coords[0][0] + coords[1][0] + coords[2][0] + coords[3][0]) / 4 + x1
                    center_y = (coords[0][1] + coords[1][1] + coords[2][1] + coords[3][1]) / 4 + y1
                    return center_x, center_y, confidence
        return -1, -1, 0