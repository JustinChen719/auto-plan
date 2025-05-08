from agent.react import ReActAgent
from core.llm import LLM, LLMName, LLMResponseContent
from tools import get_tool_mapper, FinishTool, MathTool
from utils import get_logger

logger = get_logger(__name__)


class ToolCallAgent(ReActAgent):
    name: str = "ToolCallAgent"
    description: str = "在必要时调用各种工具，比如数学计算，辅助完成目标要求。"

    def __init__(self):
        super().__init__()

        self.allowed_tool_call_names = [
            MathTool.name,
            FinishTool.name
        ]

    def create_next_step_prompt(self) -> None:
        prompt: str = self.next_step_prompt.format(query=self.current_query)
        self.current_prompt = prompt

    async def run(self, query) -> str | None:
        logger.info(f"🧰 {self.name} 开始使用工具来解决问题：{query}")
        self.reset()
        self.current_query = query
        self.current_step = 1
        while not self.finished and not self.failed and self.current_step <= self.max_step:
            self.create_next_step_prompt()
            await self.step()
            self.current_step += 1

        if self.current_step > self.max_step:
            logger.info(f"🔴 {self.name} 运行超时！")
            return None
        if self.failed:
            logger.info(f"🔴 {self.name} 运行出现错误！")
            return None
        if self.finished:
            logger.info(f"🟢 {self.name} 运行完成，结果为：{self.result}")
            return self.result
