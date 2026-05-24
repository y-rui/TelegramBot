import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

LOG_FORMAT = "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False


class MonthlyRotatingFileHandler(TimedRotatingFileHandler):
    """按月份分子目录、按日期命名文件的日志处理器

    logs/
      2026-05/
        2026-05-24.log
        2026-05-25.log
    """

    def __init__(self, log_dir: str = "logs"):
        self._log_dir = log_dir
        filename = self._build_filename()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        super().__init__(
            filename=filename,
            when="midnight",
            interval=1,
            backupCount=90,
            encoding="utf-8",
        )
        self.suffix = "%Y-%m-%d"

    def _build_filename(self) -> str:
        now = datetime.now()
        month_dir = now.strftime("%Y-%m")
        date_name = now.strftime("%Y-%m-%d")
        return os.path.join(self._log_dir, month_dir, f"{date_name}.log")

    def doRollover(self):
        self.baseFilename = os.path.abspath(self._build_filename())
        os.makedirs(os.path.dirname(self.baseFilename), exist_ok=True)
        if self.stream:
            self.stream.close()
            self.stream = None
        if not self.delay:
            self.stream = self._open()
        super().doRollover()


def setup_logging(level: int = logging.INFO, log_dir: str | None = None) -> None:
    """配置日志，同时输出到 stdout 和按日期组织的文件。"""
    global _initialized
    if _initialized:
        return
    _initialized = True

    root = logging.getLogger()
    root.setLevel(level)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    access_formatter = logging.Formatter(
        fmt="%(asctime)s | ACCESS | %(message)s", datefmt=LOG_DATE_FORMAT
    )

    # stdout handler（所有日志）
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(formatter)
    root.addHandler(stream)

    # 文件 handler（按月份分子目录、按日期命名）
    if log_dir:
        from datetime import datetime
        now = datetime.now()
        month_dir = now.strftime("%Y-%m")
        date_name = now.strftime("%Y-%m-%d")
        filepath = os.path.join(log_dir, month_dir, f"{date_name}.log")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        file_handler = MonthlyRotatingFileHandler(log_dir)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    # 抑制第三方库 DEBUG 日志
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
