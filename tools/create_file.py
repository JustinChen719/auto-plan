import os

from tools import BaseTool
from utils import get_logger

logger = get_logger(__name__)


class CreateFileTool(BaseTool):
    """
    数学计算工具，用于计算数学问题。
    """

    name = "CreateFileTool"
    description = "文件创建工具，用于创建文件到workspace目录，主要是创建文本类型的文件。"
    parameters: dict = {
        "type": "object",
        "properties": {
            "file_name": {
                "type": "string",
                "description": "文件名，需要写到文件类型后缀，比如： ***.txt 或者 ***.md",
            },
            "file_content": {
                "type": "string",
                "description": "文件内容，需要是字符串类型",
            }
        },
        "required": ["file_name", "file_content"]
    }

    def check_params(self, params: dict) -> bool:
        if "file_name" not in params:
            return False
        if "file_content" not in params:
            return False
        return True

    async def execute(self, params: dict) -> str | None:
        root_dir = "workspace"
        file_name: str = params.get("file_name")
        file_content: str = params.get("file_content")
        logger.info(f"📂 {self.name} 正在创建文件：{file_name}")
        try:
            with open(
                    file=os.path.join(root_dir, file_name),
                    mode="w",
                    encoding="utf-8"
            ) as f:
                f.write(file_content)
            return "文件创建成功"
        except Exception as e:
            logger.error(f"🔴 {self.name} 执行错误：{e}")
            return None
