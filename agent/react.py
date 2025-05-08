from abc import abstractmethod, ABC

from core.llm import LLM, LLMName, LLMResponseContent
from tools import get_tool_mapper, FinishTool
from agent.base import BaseAgent
from utils import get_logger

logger = get_logger(__name__)


class ReActAgent(BaseAgent, ABC):
    """
    Reasoning Action Agent
    """

    def __init__(self):
        super().__init__()

        # 工具调用agent 允许调用的tool
        self.allowed_tool_call_names: list[str] = []
        # 结果
        self.result: None | str = None

        self.llm = LLM(LLMName.QWEN3_32B)

    def reset(self) -> None:
        self.current_query = None
        self.current_step = 0
        self.memory.clear()
        self.finished = False
        self.failed = False
        self.result = None
        if self.system_prompt:
            self.memory.add_system_message(self.system_prompt)

    async def think(self) -> LLMResponseContent:
        logger.info(f"🧠 {self.name} Step【{self.current_step}/{self.max_step}】 正在思考中...")
        self.memory.add_user_message(content=self.current_prompt)

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

    async def act(
            self,
            tool_call_id: str,
            tool_call_name: str,
            tool_call_params: dict
    ) -> None | str:
        """
        工具调用
        """

        if tool_call_name not in self.allowed_tool_call_names:
            raise ValueError(f"智能体 {self.name} 没有 {tool_call_name} 这个工具！")

        tool_mapper = get_tool_mapper()
        if tool_call_name in tool_mapper:
            tool = tool_mapper[tool_call_name]

            # 检查参数
            if tool.check_params(tool_call_params):
                logger.info(f"⚙️ {tool_call_name} 工具被调用！")
                tool_response = await tool.execute(tool_call_params)

                if tool_response is None:
                    logger.info(f"🔴 {tool_call_name} 工具执行失败！")
                    self.failed = True
                    return None

                # 是否调用了结束工具
                if tool_call_name == FinishTool.name:
                    self.finished = True
                    self.result = tool_response

                self.memory.add_tool_message(
                        content=tool_response,
                        tool_call_id=tool_call_id
                )
                return tool_response
            else:
                raise ValueError(f"调用 {tool_call_name} 时提供的参数 {tool_call_params} 有问题！")
        else:
            raise ValueError(f"没有 {tool_call_name} 这个工具！")

    async def step(self) -> LLMResponseContent:
        # 思考
        response: LLMResponseContent = await self.think()

        # 执行工具
        for tool_call in response.tool_calls:
            await self.act(
                    tool_call_id=tool_call.id,
                    tool_call_name=tool_call.name,
                    tool_call_params=tool_call.arguments
            )
        return response
