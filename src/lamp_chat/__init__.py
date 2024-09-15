from rich_structlog import setup_logging

setup_logging(
    log_level="INFO",
    pkg2loglevel={
        "aiosqlite": "ERROR",
    },
)
