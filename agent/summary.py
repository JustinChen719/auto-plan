from agent.base import BaseAgent
from core.llm import LLMName, LLM, LLMResponseContent
from tools import get_tool_mapper, CreateFileTool
from utils import get_logger

logger = get_logger(__name__)


class SummaryAgent(BaseAgent):
    name: str = "SummaryAgent"
    description: str = "总结者，根据目标和当前执行状态、执行结果，给出总结作为最终交给用户的答复。"

    def __init__(self):
        super().__init__()

        self.llm = LLM(LLMName.QWEN_TURBO)

    def reset(self) -> None:
        self.current_query = None
        self.current_results = None
        self.current_step = 0
        self.memory.clear()
        self.finished = False
        self.failed = False
        if self.system_prompt:
            self.memory.add_system_message(self.system_prompt)

    def create_next_step_prompt(self) -> None:
        if self.current_results is not None:
            results = "\n".join(self.current_results)
        else:
            results = ""
        prompt: str = self.next_step_prompt.format(
                query=self.current_query,
                results=results
        )
        self.current_prompt = prompt

    async def think(self) -> LLMResponseContent:
        self.memory.add_user_message(content=self.current_prompt)

        # 获取回复内容
        response: LLMResponseContent = await self.llm.response(
                memory=self.memory,
                tools=[CreateFileTool.get_tool_call_params()],
                tool_choice={"type": "function", "function": {"name": "CreateFileTool"}},  # 强制使用
                enable_thinking=False,
                display_reasoning_content=False,
                display_content=False,
        )
        self.memory.add_assistant_message(content=response.content)
        return response

    async def step(self) -> LLMResponseContent:
        response = await self.think()
        return response

    async def run(self, query: str, results: list[str]) -> LLMResponseContent:
        logger.info(f"📝 {self.name} 正在总结结果...")

        self.current_query = query
        self.current_results = results

        # 只执行一步
        self.create_next_step_prompt()
        response: LLMResponseContent = await self.step()

        # 保存文件
        if len(response.tool_calls) == 0:
            logger.info(f"🟡 {self.name} 未调用工具 {"CreateFileTool"}")
        else:
            tool_mapper = get_tool_mapper()
            create_file_tool = tool_mapper.get("CreateFileTool")
            for tool_call in response.tool_calls:
                if tool_call.name == "CreateFileTool":
                    await create_file_tool.execute(tool_call.arguments)
        return response
