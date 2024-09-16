import logging
from typing import Union, Literal

# Define a type for logging levels
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class CustomLogger:
    def __init__(
        self, name: str = "FolderSyncer", level: Union[int, LogLevel] = logging.INFO
    ):
        self.logger: logging.Logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:
            handler: logging.StreamHandler = logging.StreamHandler()
            formatter: logging.Formatter = logging.Formatter(
                # "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                "%(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def set_level(self, level: Union[int, LogLevel]) -> None:
        self.logger.setLevel(level)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)


def get_logger(name: str = "FolderSyncer") -> CustomLogger:
    logger = CustomLogger(name)
    return logger
