from tools.base import BaseTool
from utils import get_logger

logger = get_logger(__name__)


class UserInputTool(BaseTool):
    """
    用户输入工具，用于向人类（用户）提问，以获取必要信息。
    """

    name: str = "UserInputTool"
    description: str = "用户输入工具，用于向人类（用户）提问，以获取必要信息。"
    parameters: dict = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "需要询问用户的问题",
            }
        },
        "required": ["question"]
    }

    def check_params(self, params: dict) -> bool:
        if "question" not in params:
            return False
        return True

    async def execute(self, params: dict) -> str | None:
        if self.check_params(params):
            logger.info(f"💬 UserInputTool: {params['question']}")
            user_input = input()
            return user_input
        return None
