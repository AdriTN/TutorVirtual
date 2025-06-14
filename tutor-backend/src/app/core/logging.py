import logging
import sys

import structlog

def setup_logging(level: str = "INFO") -> None:
    """
    Configura el logger raíz de Python y structlog.
    - force=True: elimina handlers previos (pytest, etc.) y reaplica el nuestro.
    - level: puede ser nombre de nivel ("INFO","DEBUG",…) o constante int.
    """
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(asctime)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,           # <–– aquí está la clave
    )

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(level),
        processors=[
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer,
        ],
    )
