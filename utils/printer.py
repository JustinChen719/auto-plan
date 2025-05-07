# import json
#
# from collections import defaultdict
# from typing import Optional
# from pydantic import BaseModel, Field
# from openai import Stream
# from openai.types.chat import ChatCompletionChunk, ChatCompletion
#
#
# class Printer:
#     """
#     统一输出
#     """
#
#     @classmethod
#     async def print_message(cls, message: Stream[ChatCompletionChunk] | ChatCompletion) -> LLMResponseContent:
#         ret = LLMResponseContent()
#         if isinstance(message, Stream):
#             for chunk in message:
#                 delta = chunk.choices[0].delta
#                 if hasattr(delta, "tool_calls") and delta.tool_calls:
#                     for tool_call in delta.tool_calls:
#                         if tool_call.id:
#                             ret.tool_calls[tool_call.index]["id"] = tool_call.id
#                             ret.tool_calls[tool_call.index]["arguments"] = ""
#                         if tool_call.function.name:
#                             ret.tool_calls[tool_call.index]["name"] = tool_call.function.name
#                         if tool_call.function.arguments:
#                             ret.tool_calls[tool_call.index]["arguments"] += tool_call.function.arguments
#                 if hasattr(delta, "content") and delta.content:
#                     ret.content += delta.content
#                     print(delta.content, flush=True, end="")
#                 if hasattr(delta, "reasoning_content") and delta.reasoning_content:
#                     ret.reasoning_content += delta.reasoning_content
#                     print(delta.reasoning_content, flush=True, end="")
#
#             for tool_call in ret.tool_calls.values():
#                 tool_call["arguments"] = json.loads(tool_call["arguments"])
#
#         return ret
