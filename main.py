# main.py
import threading
from loguru import logger
from game_components.game_automation import GameAutomation
from utils.log_flush import show_log_window

def run_automation():
    logger.info("===== 游戏自动化系统启动 =====")
    try:
        automation = GameAutomation()
        automation.main_loop()
    except Exception as e:
        logger.exception(f"自动化异常: {e}")
    finally:
        automation.cleanup()
        logger.info("===== 游戏自动化系统已停止 =====")

if __name__ == "__main__":
    threading.Thread(target=run_automation, daemon=True).start()
    show_log_window()
