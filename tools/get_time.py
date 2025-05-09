import time

from tools import BaseTool
from utils import get_logger

logger = get_logger(__name__)


class GetTimeTool(BaseTool):
    name = "GetTimeTool"
    description = "用于获取当前时间。"
    parameters: dict = {
        "type": "object",
        "properties": {
        },
        "required": []
    }

    def check_params(self, params: dict) -> bool:
        return True

    async def execute(self, params: dict) -> str:
        logger.info(f"🗓️ {self.name} 获取时间")
        return "当前时间是：" + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
