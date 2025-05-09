from agent.base import BaseAgent
from agent.react import ReActAgent
from core.llm import LLM, LLMName, LLMResponseContent
from tools import FinishTool
from utils import get_logger

logger = get_logger(__name__)


class PlannerAgent(BaseAgent):
    name: str = "PlannerAgent"
    description: str = "规划器，根据问题，给出一个规划方案。"

    def __init__(self, agent_mapper: dict[str, ReActAgent]):
        super().__init__()

        # 功能性智能体映射集
        self.agent_mapper: dict[str, ReActAgent] = agent_mapper

        self.llm = LLM(LLMName.QWEN3_235B_A22B)

    def reset(self) -> None:
        self.current_query = None
        self.current_results = None
        self.current_step = 0
        self.memory.clear()
        self.finished = False
        self.failed = False
        if self.system_prompt:
            self.memory.add_system_message(self.system_prompt)

    def add_agent_result(self, call_id: str, result: str) -> None:
        """
        将agent调用结果，以tool_call的方式保存
        """

        self.memory.add_tool_message(
                content=result,
                tool_call_id=call_id
        )

    def create_next_step_prompt(self) -> None:
        prompt: str = self.next_step_prompt.format(
                query=self.current_query
        )
        self.current_prompt = prompt

    async def think(self) -> LLMResponseContent:
        self.memory.add_user_message(content=self.current_prompt)

        # 设置 agents
        agents = [agent.get_tool_call_like_params() for agent in self.agent_mapper.values()]
        agents.append(FinishTool.get_tool_call_params())  # 添加 finish 工具

        # 获取回复内容
        response: LLMResponseContent = await self.llm.response(
                memory=self.memory,
                tools=agents,
                display_reasoning_content=False,
                display_content=False
        )
        self.memory.add_assistant_message(content=response.content, tool_calls=response.tool_calls)
        return response

    async def step(self) -> LLMResponseContent:
        response: LLMResponseContent = await self.think()
        return response

    async def run(self, query: str, results: list[str] = None) -> LLMResponseContent:
        logger.info(f"🤔 {self.name} 正在思考...")

        self.current_query = query
        self.current_results = results

        # 只执行一步
        self.create_next_step_prompt()
        response: LLMResponseContent = await self.step()
        logger.info(f"💡 {self.name} 完成")
        return response
