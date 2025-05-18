from pynput import keyboard

class KeyboardListener:
    def __init__(self, toggle_pause_callback):
        self.toggle_pause_callback = toggle_pause_callback
        self.listener = keyboard.Listener(
            on_press=self.on_key_press)

    def on_key_press(self, key):
        """处理键盘按键事件"""
        try:
            if key == keyboard.Key.f11:
                self.toggle_pause_callback()
        except AttributeError:
            pass

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()