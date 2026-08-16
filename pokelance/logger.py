from __future__ import annotations

import datetime
import enum
import json
import logging
import logging.config
import os
import pathlib
import sys
import traceback
import typing as t
from logging.handlers import RotatingFileHandler

if t.TYPE_CHECKING:
    from types import TracebackType

__all__: tuple[str, ...] = (
    "DailyRotatingFileHandler",
    "JSONFormatter",
    "LogLevelColors",
    "RelativePathFilter",
    "TextFormatter",
    "handle_exception",
    "setup_logging",
)

logger = logging.getLogger(__name__)

BASE_DICT_ATTRS: tuple[str, ...] = (
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "taskName",
)


class LogLevelColors(enum.StrEnum):
    """Colors for the log levels."""

    DEBUG = "\033[96m"
    INFO = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[33m"
    CRITICAL = "\033[91m"
    ENDC = "\033[0m"

    @classmethod
    def from_level(cls, level: str) -> str:
        return getattr(cls, level.upper(), cls.ENDC)


class RelativePathFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.pathname = record.pathname.replace(os.getcwd(), "~")
        return True


def _pass_args(args: t.Sequence[t.Any], msg: str) -> str:
    msg = str(msg)
    if args:
        msg = msg % tuple(args)
    return msg


class TextFormatter(logging.Formatter):
    """Human-readable inline log formatter."""

    def __init__(
        self,
        fmt: str = "[%(asctime)s] | %(pathname)s:%(lineno)d | %(levelname)s | %(message)s",
        datefmt: str = "%Y-%m-%d %H:%M:%S",
        use_colors: bool = True,
    ) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        if self.use_colors:
            color = LogLevelColors.from_level(record.levelname)
            return f"{color}{formatted}{LogLevelColors.ENDC}"
        return formatted


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter."""

    def __init__(
        self,
        *,
        datefmt: str = "%Y-%m-%d %H:%M:%S",
        use_colors: bool = True,
    ) -> None:
        super().__init__("%(levelname)s %(name)s %(message)s", datefmt=datefmt)
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        json_log: dict[str, t.Any] = {
            "asctime": self.formatTime(record, self.datefmt),
            "levelname": (
                record.levelname
                if not self.use_colors
                else f"{LogLevelColors.from_level(record.levelname)}{record.levelname}{LogLevelColors.ENDC}"
            ),
            "name": f"{record.name}",
            "log_location": f"{record.name}.{record.funcName}:{record.lineno}",
            "message": record.getMessage(),
        }
        if record.exc_info:
            exc_type, exc_value, exc_traceback = record.exc_info
            json_log["exception"] = {
                "exc_type": getattr(exc_type, "__name__", str(exc_type)),
                "exc_value": str(exc_value),
                "traceback": traceback.format_exception(exc_type, exc_value, exc_traceback),
            }

        for attr in record.__dict__:
            if attr not in BASE_DICT_ATTRS:
                if attr == "color_message" and self.use_colors:
                    json_log["message"] = _pass_args(record.args, getattr(record, attr))  # type: ignore
                elif attr == "color_message" and not self.use_colors:
                    pass
                else:
                    json_log[attr] = getattr(record, attr)

        formatted = json.dumps(json_log, indent=4)
        return formatted.replace("\\u001b", "\033").replace("\u001b", "\033")


class DailyRotatingFileHandler(RotatingFileHandler):
    """A file handler that writes log messages to daily rotating files."""

    def __init__(
        self,
        filename: str | os.PathLike[str],
        mode: str = "a",
        maxBytes: int = 10 * 1024 * 1024,
        backupCount: int = 5,
        encoding: str | None = "utf-8",
        delay: bool = False,
        errors: str | None = None,
        structured: bool = True,
        *,
        folder: pathlib.Path | str = "logs",
    ) -> None:
        self._last_entry = datetime.datetime.today()
        self.folder = pathlib.Path(folder)
        self.filename = filename
        self.folder.mkdir(exist_ok=True)
        super().__init__(
            self.folder / f"{datetime.datetime.today().strftime('%Y-%m-%d')}-{self.filename}.log",
            mode=mode,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay,
            errors=errors,
        )
        self.setFormatter(JSONFormatter(use_colors=False) if structured else TextFormatter(use_colors=False))
        self.addFilter(RelativePathFilter())

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        if self._last_entry.date() != datetime.datetime.today().date():
            self._last_entry = datetime.datetime.today()
            self.close()
            self.baseFilename = (
                self.folder / f"{self._last_entry.strftime('%Y-%m-%d')}-{self.filename}.log"
            ).as_posix()
            self.stream = self._open()
        super().emit(record)


def handle_exception(
    exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None
) -> None:
    """Global unhandled exception hook handler."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


def setup_logging(
    log_level: int = logging.INFO,
    structured: bool = False,
    file_logging: bool = False,
    filename: str = "pokelance",
    log_dir: str | pathlib.Path = "logs",
    set_excepthook: bool = True,
) -> None:
    """Set up logging for console and optional file handlers on pokelance namespace."""
    console_formatter = "json_colored" if structured else "text_colored"
    file_formatter = "json_plain" if structured else "text_plain"

    handlers: dict[str, dict[str, t.Any]] = {
        "console": {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": console_formatter,
            "filters": ["relative_path"],
            "stream": "ext://sys.stderr",
        },
    }

    if file_logging:
        handlers["file"] = {
            "()": DailyRotatingFileHandler,
            "level": log_level,
            "formatter": file_formatter,
            "filename": filename,
            "folder": str(log_dir),
            "structured": structured,
        }

    logging_config: dict[str, t.Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "relative_path": {
                "()": RelativePathFilter,
            },
        },
        "formatters": {
            "text_colored": {
                "()": TextFormatter,
                "use_colors": True,
            },
            "text_plain": {
                "()": TextFormatter,
                "use_colors": False,
            },
            "json_colored": {
                "()": JSONFormatter,
                "use_colors": True,
            },
            "json_plain": {
                "()": JSONFormatter,
                "use_colors": False,
            },
        },
        "handlers": handlers,
        "loggers": {
            "pokelance": {
                "handlers": list(handlers.keys()),
                "level": log_level,
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)

    if set_excepthook:
        sys.excepthook = handle_exception
