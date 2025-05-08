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


async def main():
    # 主循环
    while True:
        try:
            # 用户
            logger.info("🤖 请输入问题，让智能体帮你解决吧：")
            query = input()
            if not query.strip():
                break

            await scheduler.run(query)
            await asyncio.sleep(1)

        except KeyboardInterrupt as e:
            logger.error("退出")
            break


if __name__ == '__main__':
    init()
    asyncio.run(main())
