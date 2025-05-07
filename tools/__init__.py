from tools.base import BaseTool
from tools.user_input import UserInputTool
from tools.finish import FinishTool

user_input_tool: UserInputTool = UserInputTool()
finish_tool: FinishTool = FinishTool()

# 工具（名称-实例）映射
tool_mapper: dict[str, BaseTool] = {
    user_input_tool.name: user_input_tool,
    finish_tool.name: finish_tool
}


def get_tool_mapper() -> dict[str, BaseTool]:
    return tool_mapper
