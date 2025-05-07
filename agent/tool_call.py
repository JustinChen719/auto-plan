from abc import abstractmethod

from agent.base import BaseAgent


class ToolCallAgent(BaseAgent):
    """
    工具调用Agent
    """

    def __init__(self):
        super().__init__()

        # 工具调用agent 允许调用的tool
        self.allowed_tool_call_names: list[str] = []
        # 结果
        self.result: None | str = None

    def reset(self) -> None:
        self.current_query = None
        self.current_step = 0
        self.memory.clear()
        self.finished = False
        self.failed = False
        self.result = None
        if self.system_prompt:
            self.memory.add_system_message(self.system_prompt)

    @abstractmethod
    async def tool_call(
            self,
            tool_call_id: str,
            tool_call_name: str,
            tool_call_params: dict
    ):
        pass
