from PIL import ImageGrab

class ScreenshotHandler:
    def take_screenshot(self, x1, y1, x2, y2):
        """在指定区域内截图"""
        return ImageGrab.grab(bbox=(x1, y1, x2, y2))