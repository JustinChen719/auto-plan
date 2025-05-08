from tools import BaseTool
from utils import get_logger

logger = get_logger(__name__)


class MathTool(BaseTool):
    """
    数学计算工具，用于计算数学问题。
    """

    name = "MathTool"
    description = "数学计算工具，用于计算基础数学运算。"
    parameters: dict = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "数学算式，如：2+2*3",
            }
        },
        "required": ["question"]
    }

    def check_params(self, params: dict) -> bool:
        if "question" not in params:
            return False
        return True

    async def execute(self, params: dict) -> str | None:
        question = params["question"]
        logger.info(f"🧮 {self.name} 执行：{question}")
        try:
            result = eval(question)
            return str(result)
        except Exception as e:
            logger.error(f"🔴 {self.name} 执行错误：{e}")
            return None
