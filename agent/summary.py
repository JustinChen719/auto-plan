from agent.base import BaseAgent
from core.llm import LLMName, LLM, LLMResponseContent
from utils import get_logger

logger = get_logger(__name__)


class SummaryAgent(BaseAgent):
    name: str = "SummaryAgent"
    description: str = "总结者，根据目标和当前执行状态、执行结果，给出总结作为最终交给用户的答复。"

    def __init__(self):
        super().__init__()
        self.current_results: list[str] = []

        self.memory.add_system_message(self.system_prompt)
        self.llm = LLM(LLMName.QWEN3_32B)

    def reset(self) -> None:
        self.current_query = None
        self.current_results = []
        # self.current_step = 0
        self.memory.clear()
        self.finished = False
        self.failed = False
        if self.system_prompt:
            self.memory.add_system_message(self.system_prompt)

    async def think(self) -> LLMResponseContent:
        # 设置 prompt
        prompt: str = self.next_step_prompt.format(
                query=self.current_query,
                results="\n".join(self.current_results))
        self.memory.add_user_message(content=prompt)

        # 获取回复内容
        response: LLMResponseContent = await self.llm.response(
                memory=self.memory,
                display_reasoning_content=False,
                display_content=False,
        )
        self.memory.add_assistant_message(content=response.content)
        return response

    async def step(self) -> LLMResponseContent:
        response = await self.think()
        return response

    async def run(self, query: str, results: list[str]) -> LLMResponseContent:
        logger.info(f"✨️ {self.name} 正在总结结果...")

        self.current_query = query
        self.current_results = results

        # 只执行一步
        response: LLMResponseContent = await self.step()
        logger.info(f"📝 {self.name} 总结结果：\n{response}")
        return response
