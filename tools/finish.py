from tools import BaseTool


class FinishTool(BaseTool):
    """
    完成任务，适用于所有ToolCall类型Agent，用于结束Agent会话、将目标结果返回
    """

    name: str = "FinishTool"
    description: str = "顺利完成，结束对话，返回目标要求的结果"
    parameters: dict = {
        "type": "object",
        "properties": {
            "result": {
                "type": "string",
                "description": "目标对应的结果",
            }
        },
        "required": ["result"]
    }

    def check_params(self, params: dict) -> bool:
        if "result" not in params:
            return False
        return True

    async def execute(self, params: dict) -> str | None:
        return params["result"]
