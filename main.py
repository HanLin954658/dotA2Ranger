# main.py
import os
import sys

from PyQt5 import QtCore, QtWidgets, QtGui
from loguru import logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from config.config_loader import load_config, save_config
from game_components.game_automation import GameAutomation, GameAutomationWorker

# 设置日志路径
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, 'game_automation.log')
logger.remove()
# 确保日志系统初始化
logger.add(
    LOG_PATH,
    level='INFO',
    format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}',
    encoding='utf-8',
    rotation='100 MB',
    retention='7 days',
    enqueue=False
)

class LogTailWorker(QtCore.QThread):
    log_updated = QtCore.pyqtSignal(str)

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        self._running = True

    def run(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            f.seek(0, os.SEEK_END)
            while self._running:
                line = f.readline()
                if line:
                    self.log_updated.emit(line)
                else:
                    self.msleep(200)  # sleep for 200ms

    def stop(self):
        self._running = False
        self.wait()
class LogWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("日志监控")
        self.setGeometry(0, 500, 500, 200)
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.9)

        font = QtGui.QFont("Consolas", 10)
        layout = QtWidgets.QVBoxLayout(self)

        self.text_area = QtWidgets.QPlainTextEdit(readOnly=True)
        self.text_area.setFont(font)
        self.text_area.setStyleSheet("QPlainTextEdit { background-color: black; color: lightgreen; border: none; }")
        self.text_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.text_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.text_area)

        self.log_lines = []

        # 启动 tail worker
        self.tail_thread = LogTailWorker(LOG_PATH)
        self.tail_thread.log_updated.connect(self.append_log)
        self.tail_thread.start()

    def append_log(self, line):
        self.log_lines.append(line)
        self.log_lines = self.log_lines[-10:]  # 保留最后 10 行
        self.text_area.setPlainText("".join(self.log_lines))
        self.text_area.verticalScrollBar().setValue(
            self.text_area.verticalScrollBar().maximum()
        )

    def closeEvent(self, event):
        self.tail_thread.stop()
        event.accept()



class ConfigDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("配置")
        self.setGeometry(100, 100, 300, 200)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(0.9)
        self.result_config = None
        self.init_ui()
        self.load_last_config()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.mode_box = QtWidgets.QComboBox()
        self.mode_box.addItems(["难度","开局", "收起","存档","重开" ])
        layout.addWidget(QtWidgets.QLabel("模式选择"))
        layout.addWidget(self.mode_box)

        self.gold_checkbox = QtWidgets.QCheckBox("是否开启金币消耗")
        layout.addWidget(self.gold_checkbox)

        layout.addWidget(QtWidgets.QLabel("难度"))
        slider_layout = QtWidgets.QHBoxLayout()
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(25)
        self.slider.setValue(10)
        self.slider_label = QtWidgets.QLabel(str(self.slider.value()))
        self.slider.valueChanged.connect(lambda v: self.slider_label.setText(str(v)))
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.slider_label)
        layout.addLayout(slider_layout)

        buttons_layout = QtWidgets.QHBoxLayout()
        confirm_btn = QtWidgets.QPushButton("确认")
        confirm_btn.clicked.connect(self.on_confirm)
        cancel_btn = QtWidgets.QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(confirm_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def load_last_config(self):
        conf = load_config()
        if not conf:
            return
        mode = conf.get("mode", "开局")
        if mode in [self.mode_box.itemText(i) for i in range(self.mode_box.count())]:
            self.mode_box.setCurrentText(mode)

        self.gold_checkbox.setChecked(conf.get("use_gold", False))
        self.slider.setValue(conf.get("difficulty", 10))

    def on_confirm(self):
        self.result_config = {
            "mode": self.mode_box.currentText(),
            "use_gold": self.gold_checkbox.isChecked(),
            "difficulty": self.slider.value()
        }
        save_config(self.result_config)
        self.accept()


class MainApplication(QtWidgets.QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.automation = None
        self.worker = None
        self.log_window = None

    def start_application(self):
        # 首先显示配置对话框
        dialog = ConfigDialog()
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            config = dialog.result_config
            logger.info(f"用户配置: {config}")

            # 初始化自动化系统
            self.automation = GameAutomation(config)

            # 启动日志窗口
            self.log_window = LogWindow()
            self.log_window.show()

            # 在单独的线程中启动游戏自动化
            self.worker = GameAutomationWorker(self.automation)
            self.worker.start()
        else:
            logger.info("用户取消了配置")
            self.quit()


if __name__ == "__main__":
    app = MainApplication(sys.argv)
    app.start_application()
    sys.exit(app.exec_())