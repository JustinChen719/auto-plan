import json
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Role(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    role: Role = Field(...)
    reasoning_content: Optional[str] = Field(default="")
    content: Optional[str] = Field(default="")

    # 用户消息中的可调用工具
    tools: list = Field(default_factory=list)

    # AI消息中的调用工具的调用结果
    tool_calls: list = Field(default_factory=list)

    # Tool消息中的工具调用的id
    tool_call_id: str = Field(default="")


class Memory(BaseModel):
    messages: list[Message] = []

    def add_system_message(self, content: str):
        self.messages.append(Message(role=Role.SYSTEM, content=content))

    def add_user_message(self, content: str, tools: list = []):
        self.messages.append(Message(role=Role.USER, content=content, tools=tools))

    def add_assistant_message(self, content: str, tool_calls: list["LLMToolCall"] = []):
        if len(tool_calls) > 0:
            handled_tool_calls = [
                {
                    "id": tool_call.id,
                    "function": {
                        "arguments": json.dumps(tool_call.arguments),
                        "name": tool_call.name,
                    },
                    "type": "function",
                    "index": index,
                }
                for index, tool_call in enumerate(tool_calls)
            ]
            self.messages.append(Message(role=Role.ASSISTANT, content=content, tool_calls=handled_tool_calls))
        else:
            self.messages.append(Message(role=Role.ASSISTANT, content=content))

    def add_tool_message(self, content: str, tool_call_id: str):
        self.messages.append(Message(role=Role.TOOL, content=content, tool_call_id=tool_call_id))

    def clear(self):
        self.messages = []
