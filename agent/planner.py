from agent.base import BaseAgent
from agent.tool_call import ToolCallAgent
from core.llm import LLM, LLMName, LLMResponseContent
from utils.prompt import PLANNER_JUGER_PROMPT
from utils import get_logger

logger = get_logger(__name__)


class PlannerAgent(BaseAgent):
    name: str = "PlannerAgent"
    description: str = "规划器，根据问题，给出一个规划方案。"

    def __init__(self, agent_mapper: dict[str, ToolCallAgent]):
        super().__init__()
        self.juger_prompt: str = PLANNER_JUGER_PROMPT

        # 功能性智能体映射集
        self.agent_mapper: dict[str, ToolCallAgent] = agent_mapper

        self.memory.add_system_message(self.system_prompt)
        self.llm = LLM(LLMName.QWEN3_32B)

    def reset(self) -> None:
        self.current_query = None
        # self.current_step = 0
        self.memory.clear()
        self.finished = False
        self.failed = False
        if self.system_prompt:
            self.memory.add_system_message(self.system_prompt)

    async def think(self) -> LLMResponseContent:
        # 设置 prompt
        agents = "\n".join([
            f"{agent.name}: {agent.description}" for agent in self.agent_mapper.values()
        ])
        prompt: str = self.next_step_prompt.format(
                query=self.current_query,
                results="",
                agents=agents)
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
        response: LLMResponseContent = await self.think()
        return response

    async def run(self, query) -> LLMResponseContent:
        logger.info(f"📜 {self.name} 正在制作规划方案...")

        self.current_query = query

        # 只执行一步
        response: LLMResponseContent = await self.step()
        logger.info(f"💡 {self.name} 完成了计划的制定")
        return response

    async def juger(self, query: str, results: list[str]) -> bool:
        logger.info(f"🤔 {self.name} 正在判断结果...")

        # 设置 prompt
        prompt: str = self.juger_prompt.format(
                query=query,
                results="\n".join(results)
        )
        self.memory.add_user_message(content=prompt)

        # 获取回复内容
        response: LLMResponseContent = await self.llm.response(
                memory=self.memory,
        )
        self.memory.add_assistant_message(content=response.content)

        # 处理回复内容
        can_finish = "False" not in response.content
        if can_finish:
            logger.info(f"🏁 {self.name} 判断完毕，达到目标要求")
        else:
            logger.info(f"🟡 {self.name} 判断完毕，未达到目标要求，需要尝试继续制定计划")
        return can_finish
