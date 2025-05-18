import cv2
import numpy as np
from PIL import ImageGrab

class ImageFinder:
    def __init__(self):
        pass

    def find_image_in_area(self, template_path, x1, y1, x2, y2, threshold=0.8):
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
        # 截取指定区域的屏幕截图
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
            return center_x, center_y
        else:
            return -1, -1