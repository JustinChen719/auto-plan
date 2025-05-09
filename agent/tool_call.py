from agent.react import ReActAgent
from tools import FinishTool, MathTool, GetTimeTool
from utils import get_logger

logger = get_logger(__name__)


class ToolCallAgent(ReActAgent):
    name: str = "ToolCallAgent"
    description: str = "在必要时调用各种工具，比如数学计算、获取当前时间，辅助完成目标要求。"

    def __init__(self):
        super().__init__()

        self.allowed_tool_call_names = [
            MathTool.name,
            GetTimeTool.name,
            FinishTool.name
        ]

    def create_next_step_prompt(self) -> None:
        prompt: str = self.next_step_prompt.format(query=self.current_query)
        self.current_prompt = prompt

    async def run(self, query) -> str | None:
        logger.info(f"🧰 {self.name} 开始使用工具来解决问题：{query}")
        await super().run(query)
