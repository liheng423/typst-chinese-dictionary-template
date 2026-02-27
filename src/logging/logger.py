import functools
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Dict, Optional, Union

DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_FILE = "app.log"
DEFAULT_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_BACKUP_COUNT = 3
DEFAULT_LEVEL_MODE = {
    logging.DEBUG: "verbose",
    logging.INFO: "standard",
    logging.WARNING: "standard",
    logging.ERROR: "error",
    logging.CRITICAL: "error",
}
DEFAULT_MODE_FORMATS = {
    "standard": DEFAULT_FORMAT,
    "verbose": "%(asctime)s | %(levelname)s | %(name)s | %(message)s | %(filename)s:%(lineno)d",
    "error": "%(asctime)s | %(levelname)s | %(name)s | %(message)s | %(pathname)s:%(lineno)d",
}

_CONFIGURED = False


def _env_bool(key: str, default: bool) -> bool:
    value = os.getenv(key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_level(value: Optional[Union[str, int]]) -> int:
    if value is None:
        value = os.getenv("LOG_LEVEL", "INFO")
    if isinstance(value, int):
        return value
    text = str(value).strip().upper()
    return logging._nameToLevel.get(text, logging.INFO)


def _coerce_logger(value: Optional[Union[str, logging.Logger]], default_name: str) -> logging.Logger:
    if isinstance(value, logging.Logger):
        return value
    name = value or default_name
    return logging.getLogger(name)


class LevelModeFormatter(logging.Formatter):
    def __init__(
        self,
        mode_formats: Dict[str, str],
        level_mode: Dict[int, str],
        datefmt: str = DEFAULT_DATEFMT,
        default_mode: str = "standard",
    ) -> None:
        super().__init__(datefmt=datefmt)
        self._mode_formats = dict(mode_formats)
        self._level_mode = dict(level_mode)
        self._default_mode = default_mode
        self._formatters: Dict[str, logging.Formatter] = {}

    def format(self, record: logging.LogRecord) -> str:
        mode = getattr(record, "_log_mode", None)
        if not mode:
            mode = self._level_mode.get(record.levelno, self._default_mode)
        fmt = self._mode_formats.get(mode, self._mode_formats.get(self._default_mode, DEFAULT_FORMAT))
        formatter = self._formatters.get(fmt)
        if not formatter:
            formatter = logging.Formatter(fmt=fmt, datefmt=self.datefmt)
            self._formatters[fmt] = formatter
        return formatter.format(record)


def setup_logging(
    level: Optional[Union[str, int]] = None,
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    console: Optional[bool] = None,
    fmt: str = DEFAULT_FORMAT,
    datefmt: str = DEFAULT_DATEFMT,
    level_mode: Optional[Dict[int, str]] = None,
    mode_formats: Optional[Dict[str, str]] = None,
    max_bytes: Optional[int] = None,
    backup_count: Optional[int] = None,
    force: bool = False,
) -> logging.Logger:
    global _CONFIGURED

    if _CONFIGURED and not force:
        return logging.getLogger()

    root = logging.getLogger()
    root.setLevel(_parse_level(level))

    if force:
        for handler in list(root.handlers):
            root.removeHandler(handler)

    if mode_formats is None and level_mode is None:
        formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    else:
        formatter = LevelModeFormatter(
            mode_formats=mode_formats or DEFAULT_MODE_FORMATS,
            level_mode=level_mode or DEFAULT_LEVEL_MODE,
            datefmt=datefmt,
        )

    if console is None:
        console = _env_bool("LOG_CONSOLE", True)

    if console:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        root.addHandler(stream_handler)

    file_path = log_file or os.getenv("LOG_FILE")
    log_dir = log_dir or os.getenv("LOG_DIR")
    if file_path or log_dir:
        if not file_path:
            file_path = DEFAULT_LOG_FILE
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            file_path = os.path.join(log_dir, file_path)

        if max_bytes is None:
            max_bytes = int(os.getenv("LOG_MAX_BYTES", DEFAULT_MAX_BYTES))
        if backup_count is None:
            backup_count = int(os.getenv("LOG_BACKUP_COUNT", DEFAULT_BACKUP_COUNT))

        file_handler = RotatingFileHandler(
            file_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    _CONFIGURED = True
    return root


def get_logger(name: Optional[str] = None) -> logging.Logger:
    if not _CONFIGURED:
        setup_logging()
    return logging.getLogger(name)


def log_call(
    level: Optional[Union[str, int]] = None,
    logger: Optional[Union[str, logging.Logger]] = None,
    mode: Optional[str] = None,
    log_args: bool = False,
    log_result: bool = False,
):
    levelno = _parse_level(level)

    def decorator(func):
        log = _coerce_logger(logger, func.__module__)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            extra = {"_log_mode": mode} if mode else None
            if log_args:
                log.log(levelno, "call %s args=%s kwargs=%s", func.__name__, args, kwargs, extra=extra)
            else:
                log.log(levelno, "call %s", func.__name__, extra=extra)
            try:
                result = func(*args, **kwargs)
            except Exception:
                log.exception("error %s", func.__name__, extra=extra)
                raise
            if log_result:
                log.log(levelno, "done %s result=%r", func.__name__, result, extra=extra)
            else:
                log.log(levelno, "done %s", func.__name__, extra=extra)
            return result

        return wrapper

    return decorator


__all__ = ["setup_logging", "get_logger", "log_call"]
