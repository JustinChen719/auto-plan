import json

from collections import defaultdict
from enum import Enum
from openai import OpenAI, Stream
from pydantic import BaseModel, Field

from utils.schema import Message, Memory, Role
from utils import Config, get_logger

logger = get_logger(__name__)


class LLMName(Enum):
    QWEN_TURBO = "qwen-turbo"
    QWEN_PLUS = "qwen-plus"
    QWEN3_32B = "qwen3-32b"
    QWEN3_235B_A22B = "qwen3-235b-a22b"


class LLMToolCall(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    arguments: dict = Field(default_factory=dict)


class LLMResponseContent(BaseModel):
    content: str = Field(default="")
    reasoning_content: str = Field(default="")
    tool_calls: list[LLMToolCall] = Field(default_factory=list)


class LLM:
    _instances: dict[str, "LLM"] = {}

    def __new__(cls, model_name):
        if model_name not in cls._instances:
            instance = object.__new__(cls)
            instance.__init__(model_name)
            cls._instances[model_name] = instance
            return instance
        else:
            return cls._instances[model_name]

    def __init__(self, model_name: LLMName):
        self.model_name: LLMName = model_name
        self.client = OpenAI(api_key=Config.API_KEY, base_url=Config.BASE_URL)

    @staticmethod
    def memory_to_message(memory_message: Message):
        if memory_message.role == Role.USER:
            return {"role": "user", "content": memory_message.content}
        elif memory_message.role == Role.ASSISTANT:
            if memory_message.tool_calls:
                return {"role": "assistant", "content": memory_message.content, "tool_calls": memory_message.tool_calls}
            else:
                return {"role": "assistant", "content": memory_message.content}
        elif memory_message.role == Role.SYSTEM:
            return {"role": "system", "content": memory_message.content}
        elif memory_message.role == Role.TOOL:
            return {"role": "tool", "content": memory_message.content, "tool_call_id": memory_message.tool_call_id}

    async def response(
            self,
            memory: Memory,
            tools=None,
            tool_choice: str | dict = "auto",
            enable_thinking: bool = True,
            display_reasoning_content: bool = False,
            display_content: bool = False
    ) -> LLMResponseContent:
        # 重新组织对话结构
        messages = []
        for message in memory.messages:
            messages.append(self.memory_to_message(message))

        # 生成结果
        response = self.client.chat.completions.create(
                model=self.model_name.value,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                extra_body={"enable_thinking": enable_thinking},
                parallel_tool_calls=True,
                stream=True
        )

        # 解析结果
        response_content = LLMResponseContent()
        tool_calls: dict[int, dict] = defaultdict(dict)  # 临时存储
        if isinstance(response, Stream):
            for chunk in response:
                delta = chunk.choices[0].delta
                if hasattr(delta, "tool_calls") and delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        """ {id, name, arguments} """
                        if tool_call.id:
                            tool_calls[tool_call.index]["id"] = tool_call.id
                            tool_calls[tool_call.index]["arguments"] = ""
                        if tool_call.function.name:
                            tool_calls[tool_call.index]["name"] = tool_call.function.name
                        if tool_call.function.arguments:
                            tool_calls[tool_call.index]["arguments"] += tool_call.function.arguments
                if hasattr(delta, "content") and delta.content:
                    response_content.content += delta.content
                    if display_content:
                        print(delta.content, flush=True, end="")
                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    response_content.reasoning_content += delta.reasoning_content
                    if display_reasoning_content:
                        print(delta.reasoning_content, flush=True, end="")
            if display_reasoning_content or display_content:
                print("\n")

            # json解析
            tool_calls_list = [(index, value) for index, value in tool_calls.items()]
            tool_calls_list.sort(key=lambda x: x[0])
            for tool_call in tool_calls_list:
                try:
                    response_content.tool_calls.append(
                            LLMToolCall(
                                    id=tool_call[1]["id"],
                                    name=tool_call[1]["name"],
                                    arguments=json.loads(tool_call[1]["arguments"]),
                            )
                    )
                except Exception as e:
                    logger.error(e)
                    logger.error(tool_call[1])

        return response_content
