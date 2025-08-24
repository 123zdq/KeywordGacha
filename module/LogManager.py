import logging
from logging.handlers import TimedRotatingFileHandler
from os import makedirs
from threading import Lock
from traceback import format_exception
from typing import Any, Self

from rich.console import Console
from rich.logging import RichHandler
from rich.status import Status


class LogManager:
    __PATH: str = "./log"
    __instance = None
    __lock = Lock()

    def __init__(self) -> None:
        super().__init__()

        # 控制台实例
        self.console = Console()

        # 文件日志实例
        makedirs(__class__.__PATH, exist_ok=True)
        self.file_handler = TimedRotatingFileHandler(
            f"{__class__.__PATH}/app.log",
            when="midnight",
            interval=1,
            encoding="utf-8",
            backupCount=3,
        )
        self.file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        self.file_logger = logging.getLogger("keywordgacha_file")
        self.file_logger.propagate = False
        self.file_logger.setLevel(logging.DEBUG)
        self.file_logger.addHandler(self.file_handler)

        # 控制台日志实例
        self.console_handler = RichHandler(
            markup=True,
            show_path=False,
            rich_tracebacks=False,
            tracebacks_extra_lines=0,
            log_time_format="[%X]",
            omit_repeated_times=False,
        )
        self.console_logger = logging.getLogger("keywordgacha_console")
        self.console_logger.propagate = False
        self.console_logger.setLevel(logging.INFO)
        self.console_logger.addHandler(self.console_handler)

        levels = ["debug", "info", "warning", "error"]
        self._file_methods = {level: getattr(self.file_logger, level) for level in levels}
        self._console_methods = {level: getattr(self.console_logger, level) for level in levels}
        # self._file_methods["print"] = self.file_logger.info
        # self._console_methods["print"] = self.console.print

    # 日志管理器的单例实例
    @classmethod
    def get(cls) -> Self:
        if cls.__instance is None:
            with cls.__lock:
                if cls.__instance is None:
                    cls.__instance = cls()
        return cls.__instance

    def is_expert_mode(self) -> bool:
        if getattr(self, "expert_mode", None) is None:
            with __class__.__lock:
                if getattr(self, "expert_mode", None) is None:
                    self.expert_mode = True  # Import Config !!!
                    if self.expert_mode:
                        self.console_logger.setLevel(logging.DEBUG)
        return self.expert_mode

    def _log(self, level: str, msg: str, e: Exception | None = None, file: bool = True, console: bool = True) -> None:
        file_method = self._file_methods[level]
        console_method = self._console_methods[level]
        if e is None:
            if file:
                file_method(msg)
            if console:
                console_method(msg)
        else:
            msg_e = f"{msg} {e}" if msg != "" else str(e)
            full_msg = f"{msg_e}\n{self.get_trackback(e)}\n"
            if file:
                file_method(full_msg)
            if console:
                console_method(full_msg if self.is_expert_mode() else msg_e)

    def debug(self, msg: str, e: Exception | None = None, file: bool = True, console: bool = True) -> None:
        self._log("debug", msg, e, file, console)

    def info(self, msg: str, e: Exception | None = None, file: bool = True, console: bool = True) -> None:
        self._log("info", msg, e, file, console)

    def warning(self, msg: str, e: Exception | None = None, file: bool = True, console: bool = True) -> None:
        self._log("warning", msg, e, file, console)

    def error(self, msg: str, e: Exception | None = None, file: bool = True, console: bool = True) -> None:
        self._log("error", msg, e, file, console)

    def get_trackback(self, e: Exception) -> str:
        return "".join(format_exception(e)).strip()

    # def print(self, msg: str, e: Exception | None = None, file: bool = True, console: bool = True) -> None: self._log("print", msg, e, file, console)
    def print(self, *args: Any, **kwargs: Any) -> None:
        self.console.print(*args, **kwargs)

    def status(self, msg: str) -> Status:
        return self.console.status(msg)

    def rule(self, *args: Any, **kwargs: Any) -> None:
        self.console.rule(*args, **kwargs)
