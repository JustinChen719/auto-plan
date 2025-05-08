from abc import abstractmethod, ABC

from core.llm import LLM
from utils.prompt import SYSTEM_PROMPTS, NEXT_STEP_PROMPTS
from utils.schema import Memory


class BaseAgent(ABC):
    name: str = "BaseAgent"
    description: str = "BaseAgent"

    def __init__(self):
        self.system_prompt = SYSTEM_PROMPTS.get(self.name)
        self.next_step_prompt = NEXT_STEP_PROMPTS.get(self.name)

        self.current_query: None | str = None
        self.current_prompt = ""
        self.current_results: None | list[str] = None
        self.memory = Memory()
        if self.system_prompt:
            self.memory.add_system_message(self.system_prompt)
        self.llm: None | LLM = None

        self.current_step: int = 0
        self.max_step: int = 10
        self.finished: bool = False
        self.failed: bool = False

    @classmethod
    def get_tool_call_like_params(cls) -> dict:
        """ 获取工具调用类似格式的agent参数 """
        return {
            "type": "function",
            "function": {
                "name": cls.name,
                "description": cls.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "需要完成的任务",
                        }
                    },
                    "required": ["task"]
                }
            },
        }

    @abstractmethod
    def reset(self) -> None:
        """
        重置状态
        """
        pass

    @abstractmethod
    def create_next_step_prompt(self) -> None:
        pass

    @abstractmethod
    async def think(self) -> None:
        """
        思考
        """
        pass

    @abstractmethod
    async def step(self) -> None:
        """
        单步
        """
        pass

    @abstractmethod
    async def run(self, *args, **kwargs) -> str:
        """
        主执行函数
        """
        pass
