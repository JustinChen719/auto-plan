from agent.tool_call import ToolCallAgent
from core.llm import LLM, LLMName, LLMResponseContent
from tools import get_tool_mapper, UserInputTool, FinishTool
from utils import get_logger

logger = get_logger(__name__)


class AskHumanAgent(ToolCallAgent):
    name: str = "AskHumanAgent"
    description: str = "在必要时向人类提问，询问得到关键信息后继续回答问题。"

    def __init__(self):
        super().__init__()

        self.allowed_tool_call_names = [
            UserInputTool.name,
            FinishTool.name
        ]

        if self.system_prompt:
            self.memory.add_system_message(self.system_prompt)
        self.llm = LLM(LLMName.QWEN3_32B)

    async def think(self) -> LLMResponseContent:
        # 设置 prompt
        prompt: str = self.next_step_prompt.format(query=self.current_query)
        self.memory.add_user_message(content=prompt)

        # 设置 tools
        tool_mapper = get_tool_mapper()
        tools = [tool_mapper[tool_name].get_tool_call_params() for tool_name in self.allowed_tool_call_names]

        # 获取回复内容
        response: LLMResponseContent = await self.llm.response(
                memory=self.memory,
                tools=tools
        )
        self.memory.add_assistant_message(content=response.content, tool_calls=response.tool_calls)
        return response

    async def tool_call(
            self,
            tool_call_id: str,
            tool_call_name: str,
            tool_call_params: dict
    ) -> None | str:
        if tool_call_name not in self.allowed_tool_call_names:
            raise ValueError(f"智能体 {self.name} 没有 {tool_call_name} 这个工具！")

        tool_mapper = get_tool_mapper()
        if tool_call_name in tool_mapper:
            tool = tool_mapper[tool_call_name]
            if tool.check_params(tool_call_params):
                logger.info(f"⚙️ {tool_call_name} 工具被调用！")
                # 结束
                if tool_call_name == FinishTool.name:
                    self.finished = True
                    self.result = await tool.execute(tool_call_params)
                    return self.result
                # 正常执行
                return await tool.execute(tool_call_params)
            else:
                raise ValueError(f"调用 {tool_call_name} 时提供的参数 {tool_call_params} 有问题！")
        else:
            raise ValueError(f"没有 {tool_call_name} 这个工具！")

    async def step(self) -> LLMResponseContent:
        # 思考
        response: LLMResponseContent = await self.think()

        # 执行工具
        for tool_call in response.tool_calls:
            response_content: str = await self.tool_call(
                    tool_call_id=tool_call.id,
                    tool_call_name=tool_call.name,
                    tool_call_params=tool_call.arguments
            )
            if response_content:
                self.memory.add_tool_message(
                        content=response_content,
                        tool_call_id=tool_call.id
                )

        return response

    async def run(self, query) -> str | None:
        logger.info(f"❔️ {self.name} 正在向用户提问：{query}")
        self.reset()
        self.current_query = query
        self.current_step = 1
        while not self.finished and not self.failed and self.current_step <= self.max_step:
            await self.step()
            self.current_step += 1

        if self.failed:
            logger.info(f"🔴 {self.name} 运行出现错误！")
            return None
        if self.finished:
            logger.info(f"🟢 {self.name} 运行完成，结果为：{self.result}")
            return self.result
