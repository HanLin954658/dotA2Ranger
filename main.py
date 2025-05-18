"""
游戏自动化系统的主入口点，负责初始化自动化流程并处理异常情况。
"""
from loguru import logger

from game_components.game_automation import GameAutomation

if __name__ == "__main__":
    logger.info("===== 游戏自动化系统启动 =====")
    logger.info("初始化游戏自动化组件...")

    try:
        # 初始化并运行自动化
        logger.debug("创建GameAutomation实例")
        automation = GameAutomation()

        logger.info("开始执行游戏自动化主循环")
        automation.main_loop()

    except KeyboardInterrupt:
        logger.warning("接收到用户中断信号，程序终止")
        print("程序已被用户终止")

    except Exception as e:
        logger.critical(f"发生意外错误: {e}", exc_info=True)

    finally:
        # 确保清理工作执行
        logger.info("执行清理操作...")
        if 'automation' in locals():
            logger.debug("调用自动化实例的清理方法")
            automation.cleanup()

        logger.info("===== 游戏自动化系统已停止 =====")