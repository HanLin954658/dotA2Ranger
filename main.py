import winsound

from gui.user_settings_gui import get_user_settings
from core.game_automation import GameAutomation

if __name__ == "__main__":
    # 获取用户设置
    #
    # try:
    #     var1, nandu, use_money = get_user_settings()
    #     print(var1, nandu, use_money)
    #     # 初始化游戏自动化类
    #     automation = GameAutomation()
    #
    #     # 启动主循环
    #     automation.main_loop()
    # except Exception as e:
    #     print(e)
    #     winsound.Beep(500, 2000)
    #     raise e







    var1, nandu, use_money = get_user_settings()
    print(var1, nandu, use_money)
    # 初始化游戏自动化类
    automation = GameAutomation()

    # 启动主循环
    automation.main_loop()