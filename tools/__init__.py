from tools.base import BaseTool
from tools.user_input import UserInputTool
from tools.finish import FinishTool
from tools.math import MathTool
from tools.create_file import CreateFileTool
from tools.get_time import GetTimeTool

user_input_tool: UserInputTool = UserInputTool()
math_tool: MathTool = MathTool()
create_file_tool: CreateFileTool = CreateFileTool()
get_time_tool: GetTimeTool = GetTimeTool()
finish_tool: FinishTool = FinishTool()

# 工具（名称-实例）映射
tool_mapper: dict[str, BaseTool] = {
    user_input_tool.name: user_input_tool,
    math_tool.name: math_tool,
    create_file_tool.name: create_file_tool,
    get_time_tool.name: get_time_tool,
    finish_tool.name: finish_tool
}


def get_tool_mapper() -> dict[str, BaseTool]:
    return tool_mapper
