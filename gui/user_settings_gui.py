import sys
from PyQt5 import QtCore, QtWidgets
from config.config_loader import load_config, save_config


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
        self.mode_box.addItems(["开局", "重开", "难度", "收起"])
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


def get_user_config(app=None):
    """
    获取用户配置

    如果传入了app参数，则使用该应用程序实例
    否则创建一个临时的应用程序实例
    """
    # 检查是否已有QApplication实例
    need_app = app is None

    if need_app:
        app = QtWidgets.QApplication(sys.argv)

    dialog = ConfigDialog()
    result = dialog.exec_()

    if result == QtWidgets.QDialog.Accepted:
        config = dialog.result_config
    else:
        config = None

    # 只有当我们创建了临时应用时才退出
    if need_app:
        app.quit()

    return config


# 仅作为独立模块测试时运行
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    config = get_user_config(app)
    if config:
        print("用户配置:", config)
    else:
        print("用户取消了配置")
    sys.exit(app.exec_())