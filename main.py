import asyncio

from core.scheduler import Scheduler
from utils import get_logger

logger = get_logger()

scheduler: None | Scheduler = None


def init():
    global scheduler

    scheduler = Scheduler()


# 帮我查看明天苏州的天气
# 帮我挑一件日常男士服装
# 帮我计算一个数学题
# 帮我计算99*8和66*9的结果，然后还要计算这两个结果之和


async def main():
    # 主循环
    while True:
        try:
            logger.info("🤖 请输入问题，让智能体帮你解决吧：")
            query = input()
            if not query.strip():
                logger.info("未输入内容，结束对话")
                break

            # 开始执行
            await scheduler.run(query)

        except KeyboardInterrupt as e:
            logger.error("退出")
            break


if __name__ == '__main__':
    init()
    asyncio.run(main())
