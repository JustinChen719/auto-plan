from abc import ABC, abstractmethod

"""
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "当你想查询指定城市的天气时非常有用。",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "城市或县区，比如北京市、杭州市、余杭区等。",
                }
            },
            "required": ["location"]
        }
    }
"""


class BaseTool(ABC):
    name: str = "BaseTool"
    description: str = "BaseTool"
    parameters: dict = {}

    @classmethod
    def get_tool_call_params(cls) -> dict:
        """ 获取工具调用参数 """
        return {
            "type": "function",
            "function": {
                "name": cls.name,
                "description": cls.description,
                "parameters": cls.parameters
            },
        }

    @abstractmethod
    def check_params(self, params: dict) -> bool:
        """ 检查参数是否合法 """

    @abstractmethod
    async def execute(self, params: dict) -> None:
        pass
