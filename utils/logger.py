import sys
from logging import Logger, DEBUG, StreamHandler, Formatter


class ColorfulFormatter(Formatter):
    LEVEL_COLORS = {
        "DEBUG": "\033[94m",  # 蓝色
        "INFO": "\033[92m",  # 绿色
        "WARNING": "\033[93m",  # 黄色
        "ERROR": "\033[91m",  # 红色
        "CRITICAL": "\033[95m",  # 紫色
        "RESET": "\033[0m"  # 重置颜色
    }

    def format(self, record):
        levelname = record.levelname
        color = self.LEVEL_COLORS.get(levelname, self.LEVEL_COLORS["RESET"])
        reset = self.LEVEL_COLORS["RESET"]
        # 使用 super().format() 保持原有格式
        message = super().format(record)
        return f"{color}{message}{reset}"


class ProLogger(Logger):
    def __init__(
            self,
            name=__name__,
            level=DEBUG,
            fmt="%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%m-%d %H:%M:%S",
    ):
        super().__init__(name, level)

        if not self.handlers:
            console_handler = StreamHandler(stream=sys.stdout)
            console_handler.setLevel(level)
            formatter = ColorfulFormatter(fmt, datefmt)
            console_handler.setFormatter(formatter)
            self.addHandler(console_handler)


def get_logger(
        name=__name__,
        level=DEBUG,
        fmt="%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%m-%d %H:%M:%S",
):
    return ProLogger(name, level, fmt, datefmt)
