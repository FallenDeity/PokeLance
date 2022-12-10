import logging
import typing as t

__all__: t.Tuple[str, ...] = ("create_logging_setup",)


class Logger(logging.Formatter):
    COLOR_CONFIGS: t.Dict[int, str] = {
        logging.DEBUG: "\x1b[33;49m",
        logging.INFO: "\x1b[32;49m",
        logging.WARNING: "\x1b[35;49m",
        logging.ERROR: "\x1b[31;49m",
        logging.CRITICAL: "\x1b[33;41;1m",
    }

    def format(self, record: logging.LogRecord) -> str:
        log_format = f"[%(asctime)s : {record.levelname.rjust(7)}] | %(message)s "

        formatter = logging.Formatter(
            "".join(
                (
                    self.COLOR_CONFIGS.get(record.levelno, "\x1b[32;49m"),
                    log_format,
                    "\x1b[0m",
                )
            )
        )
        return formatter.format(record)


def create_logging_setup(name: str) -> logging.Logger:
    _LOGGER = logging.getLogger(name)
    stream = logging.StreamHandler()
    stream.setFormatter(Logger())
    _LOGGER.addHandler(stream)
    _LOGGER.setLevel(logging.DEBUG)
    return _LOGGER
