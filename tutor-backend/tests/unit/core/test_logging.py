import logging
import sys

import pytest
import structlog

import src.core.logging as core_logging

@pytest.fixture(autouse=True)
def reset_logging(monkeypatch):
    """
    Antes de cada test:
     - Vaciamos los handlers del root logger
     - Restauramos structlog.make_filtering_bound_logger y structlog.configure
    """
    logging.root.handlers.clear()

    # Guardamos referencias originales
    orig_make = structlog.make_filtering_bound_logger
    orig_configure = structlog.configure

    yield

    # Restauramos
    structlog.make_filtering_bound_logger = orig_make
    structlog.configure = orig_configure
    logging.root.handlers.clear()


def test_setup_logging_default_level_and_handler_and_formatter(monkeypatch):
    # Interceptar structlog.configure y make_filtering...
    recorded = {}
    monkeypatch.setattr(
        structlog,
        "make_filtering_bound_logger",
        lambda lvl: f"WRAPPER_{lvl}"
    )
    monkeypatch.setattr(
        structlog,
        "configure",
        lambda **kw: recorded.update(kw)
    )

    # Llamamos con el nivel por defecto
    core_logging.setup_logging()

    # 1) el root logger debe quedar en INFO
    assert logging.root.level == logging.INFO

    # 2) Debe haber exactamente un handler, de tipo StreamHandler sobre stdout
    assert len(logging.root.handlers) == 1
    handler = logging.root.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert handler.stream is sys.stdout

    # 3) El formateador del handler debe usar el fmt configurado
    fmt = "%(levelname)s %(asctime)s %(name)s: %(message)s"
    assert handler.formatter._fmt == fmt

    # 4) structlog.configure recibió el wrapper_class correcto
    assert recorded["wrapper_class"] == "WRAPPER_INFO"

    # 5) Y la lista de processors en el orden exacto
    procs = recorded["processors"]
    # primera etapa stamp ISO
    assert isinstance(procs[0], structlog.processors.TimeStamper)
    assert procs[0].fmt == "ISO"
    # luego add_log_level
    assert procs[1] is structlog.processors.add_log_level
    # StackInfoRenderer
    assert isinstance(procs[2], structlog.processors.StackInfoRenderer)
    # format_exc_info
    assert procs[3] is structlog.processors.format_exc_info
    # JSONRenderer
    assert isinstance(procs[4], structlog.processors.JSONRenderer)


@pytest.mark.parametrize("level_name,level_const", [
    ("DEBUG", logging.DEBUG),
    ("WARNING", logging.WARNING),
    ("ERROR", logging.ERROR),
])
def test_setup_logging_custom_level_changes_root_and_wrapper(monkeypatch, level_name, level_const):
    recorded = {}
    monkeypatch.setattr(
        structlog,
        "make_filtering_bound_logger",
        lambda lvl: f"WRAPPER_{lvl}"
    )
    monkeypatch.setattr(
        structlog,
        "configure",
        lambda **kw: recorded.update(kw)
    )

    core_logging.setup_logging(level=level_name)

    # El nivel del root logger coincide con la constante
    assert logging.root.level == level_const
    # Y el wrapper_class fue invocado con ese nivel
    assert recorded["wrapper_class"] == f"WRAPPER_{level_name}"


def test_basicconfig_no_duplicates_on_repeated_calls(monkeypatch):
    """
    basicConfig sólo añade handlers si no hay ninguno.
    """
    # parcheamos structlog para no interferir
    monkeypatch.setattr(structlog, "make_filtering_bound_logger", lambda lvl: None)
    monkeypatch.setattr(structlog, "configure", lambda **kw: None)

    # Primera llamada añade uno
    core_logging.setup_logging()
    assert len(logging.root.handlers) == 1

    # Segunda llamada NO añade otro
    core_logging.setup_logging()
    assert len(logging.root.handlers) == 1


def test_logging_output_format(capsys):
    """
    Verifica que al emitir un mensaje se respeta el formato de basicConfig.
    """
    # parcheamos structlog para no interferir
    structlog.configure = lambda **kw: None

    core_logging.setup_logging(level="ERROR")
    logger = logging.getLogger("mi.test")
    logger.error("¡Fallo!")  # debe imprimirse en stdout

    captured = capsys.readouterr()
    # El mensaje debe empezar con "ERROR " y luego timestamp y nombre del logger
    assert captured.out.startswith("ERROR ")
    assert "mi.test: ¡Fallo!" in captured.out
