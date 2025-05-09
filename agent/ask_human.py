from agent.react import ReActAgent
from tools import UserInputTool, FinishTool
from utils import get_logger

logger = get_logger(__name__)


class AskHumanAgent(ReActAgent):
    name: str = "AskHumanAgent"
    description: str = "在必要时向人类提问，询问得到关键信息后继续回答问题。"

    def __init__(self):
        super().__init__()

        self.allowed_tool_call_names = [
            UserInputTool.name,
            FinishTool.name
        ]

    def create_next_step_prompt(self) -> None:
        prompt: str = self.next_step_prompt.format(query=self.current_query)
        self.current_prompt = prompt

    async def run(self, query) -> str | None:
        logger.info(f"❔️ {self.name} 正在向用户提问：{query}")
        await super().run(query)
