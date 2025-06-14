import logging
import sys

import structlog

def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(asctime)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(level),
        processors=[
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
    )

setup_logging()
