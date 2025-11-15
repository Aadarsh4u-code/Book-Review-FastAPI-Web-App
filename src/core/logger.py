import logging
import os
import sys
import json
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from pathlib import Path
from datetime import datetime, timezone
from typing import Any
import traceback

# Ensure log directory exists
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }

        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data, default=str)


class ContextFormatter(logging.Formatter):
    """Human-readable formatter with colors for console"""

    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'
    }

    def format(self, record: logging.LogRecord) -> str:

        # Compute parent directory + filename (e.g., "books/get_all_books.py")
        filepath = os.path.abspath(record.pathname)
        parent_dir = os.path.basename(os.path.dirname(filepath))
        filename = os.path.basename(filepath)
        record.parent_file = f"{parent_dir}/{filename}"

        # Add color to level name if output is a TTY (interactive console)
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            color = self.COLORS.get(record.levelname.strip('\033[0m'), self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"

        # return super().format(record)

        # Call base formatter first
        base_log = super().format(record)

        # Append structured context if available
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            extras = record.extra_data
            # duration = extras.get("duration_ms")
            client = extras.get("client") or extras.get("client_host")

            extra_info = []
            # if duration is not None:
            #     extra_info.append(f"duration={duration}ms")
            if client is not None:
                extra_info.append(f"client={client}")

            if extra_info:
                base_log = f"{base_log} | {' | '.join(extra_info)}"

        return base_log



def setup_logger(
        name: str = "src",
        level: str = "INFO",
        enable_json: bool = False,
        enable_console: bool = True
) -> logging.Logger:
    """
    Setup comprehensive logging configuration

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_json: Enable JSON structured logging
        enable_console: Enable console output
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    logger.propagate = False

    # Remove existing handlers
    logger.handlers.clear()

    # Human-readable formatter
    text_formatter = ContextFormatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(parent_file)s|%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # JSON formatter for production
    json_formatter = JSONFormatter()


    # ========================================
    # File Handler - Main Application Log
    # ========================================
    app_file_handler = TimedRotatingFileHandler(
        filename=LOG_DIR / "src.log",
        when="midnight",
        interval=1,
        backupCount=30,  # Keep 30 days
        encoding="utf-8",
        utc=True
    )
    app_file_handler.setLevel(logging.DEBUG)
    app_file_handler.setFormatter(json_formatter if enable_json else text_formatter)
    app_file_handler.suffix = "%Y-%m-%d"
    logger.addHandler(app_file_handler)

    # ========================================
    # File Handler - Error Log (ERROR and above)
    # ========================================
    error_file_handler = RotatingFileHandler(
        filename=LOG_DIR / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding="utf-8"
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(json_formatter if enable_json else text_formatter)
    logger.addHandler(error_file_handler)

    # ========================================
    # File Handler - Database Log
    # ========================================
    db_file_handler = TimedRotatingFileHandler(
        filename=LOG_DIR / "database.log",
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
        utc=True
    )
    db_file_handler.setLevel(logging.DEBUG)
    db_file_handler.setFormatter(text_formatter)
    db_file_handler.suffix = "%Y-%m-%d"

    # Add filter for database-related logs only
    db_file_handler.addFilter(lambda record: 'database' in record.name.lower() or 'sqlalchemy' in record.name.lower())
    logger.addHandler(db_file_handler)

    # ========================================
    # Console Handler
    # ========================================
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(text_formatter)
        logger.addHandler(console_handler)

    return logger


# ========================================
# Create loggers
# ========================================
logger = setup_logger(
    name="src",
    level="INFO",
    enable_json=False,  # Set to True in production
    enable_console=True
)

# Database logger
db_logger = logging.getLogger("src.database")
db_logger.setLevel(logging.DEBUG)

# SQLAlchemy logger (optional - can be verbose)
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(logging.WARNING)  # Set to INFO for SQL query logging


# ========================================
# Custom logging functions with context
# ========================================
def log_with_context(level: str, message: str, **context: Any) -> None:
    """Log message with additional context"""
    extra = {"extra_data": context}
    getattr(logger, level.lower())(message, extra=extra)


def log_http_request(method: str, url: str, status_code: int = None, duration: float = None, **extra: Any) -> None:
    """Log HTTP request with context"""
    duration_ms = round(duration * 1000, 2) if duration else None
    context = {
        "type": "http_request",
        "method": method,
        "url": str(url),
        "status_code": status_code,
        "duration_ms": duration_ms,
        **extra
    }
    message = f"{method} {url} - {status_code}"
    if duration_ms is not None:
        message += f" (duration={duration_ms} ms)"
    log_with_context("info", message, **context)


def log_database_query(operation: str, table: str, duration: float = None, **extra: Any) -> None:
    """Log database operation"""
    context = {
        "type": "database_operation",
        "operation": operation,
        "table": table,
        "duration_ms": round(duration * 1000, 2) if duration else None,
        **extra
    }
    db_logger.info(f"DB {operation} on {table}", extra={"extra_data": context})


def log_exception(exc: Exception, context: str = None, **extra: Any) -> None:
    """Log exception with full context"""
    exc_context = {
        "type": "exception",
        "exception_type": type(exc).__name__,
        "context": context,
        **extra
    }
    logger.exception(f"Exception in {context}: {exc}", extra={"extra_data": exc_context})