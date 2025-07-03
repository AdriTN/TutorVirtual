import logging
import sys

import structlog

def setup_logging(level_name: str = "INFO") -> None: # Cambiar nombre de variable para claridad
    """
    Configura el logger raíz de Python y structlog.
    - force=True: elimina handlers previos (pytest, etc.) y reaplica el nuestro.
    - level_name: nombre de nivel ("INFO","DEBUG",…)
    """
    # Obtener el nivel numérico del nombre del nivel
    numeric_level = logging.getLevelName(level_name.upper())
    if not isinstance(numeric_level, int):
        # Fallback si el nombre del nivel no es válido.
        # logging.basicConfig también haría algo similar o fallaría.
        logging.warning(f"Invalid log level name '{level_name}'. Defaulting to INFO.")
        numeric_level = logging.INFO

    logging.basicConfig(
        level=numeric_level, # Usar el nivel numérico aquí también por consistencia
        format="%(levelname)s %(asctime)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,           # <–– aquí está la clave
    )

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level), # Usar el nivel numérico
        processors=[
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
    )
