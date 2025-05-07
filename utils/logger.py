from logging import Logger, DEBUG, StreamHandler, Formatter


class ProLogger(Logger):
    def __init__(
            self,
            name=__name__,
            level=DEBUG,
            fmt="%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%m-%d %H:%M:%S"
    ):
        super().__init__(name, level)

        if not self.handlers:
            console_handler = StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(Formatter(fmt, datefmt=datefmt))
            self.addHandler(console_handler)


def get_logger(
        name=__name__,
        level=DEBUG,
        fmt="%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%m-%d %H:%M:%S"
):
    return ProLogger(name, level, fmt, datefmt)
