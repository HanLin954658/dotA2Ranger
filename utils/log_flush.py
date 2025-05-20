# log.py
import sys, os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5 import QtCore, QtWidgets, QtGui

LOG_PATH = r"D:\Dev\PycharmProjects\dota_ranger\logs\game_automation.log"
assert os.path.exists(LOG_PATH)

class LogHandler(FileSystemEventHandler):
    def __init__(self, callback): super().__init__(); self.callback = callback
    def on_modified(self, event):
        if event.src_path == LOG_PATH: self.callback()

class LogWindow(QtWidgets.QWidget):
    update_signal = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("日志监控")
        self.setGeometry(0, 500, 500, 200)
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(0.9)
        font = QtGui.QFont("MapleMono", 10)
        layout = QtWidgets.QVBoxLayout(self)
        self.text_area = QtWidgets.QPlainTextEdit(readOnly=True)
        self.text_area.setFont(font)
        self.text_area.setStyleSheet("QPlainTextEdit { background-color: black; color: lightgreen; border: none; }")
        self.text_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.text_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.text_area)
        self.update_signal.connect(self.update_log)
        self.init_watchdog()
        self.update_log()

    def init_watchdog(self):
        self.observer = Observer()
        self.observer.schedule(LogHandler(self.trigger_update), os.path.dirname(LOG_PATH))
        self.observer.start()

    def trigger_update(self): self.update_signal.emit()

    def update_log(self):
        try:
            with open(LOG_PATH, 'r', encoding='utf-8') as f:
                self.text_area.setPlainText("".join(f.readlines()[-10:]))
        except Exception as e:
            print(f"日志读取失败: {e}")

    def closeEvent(self, event):
        self.observer.stop(); self.observer.join(); event.accept()

def show_log_window():
    app = QtWidgets.QApplication(sys.argv)
    window = LogWindow()
    window.show()
    sys.exit(app.exec_())
