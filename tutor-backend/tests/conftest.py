import logging
import pytest

@pytest.fixture(autouse=True)
def reset_root_logger():
    """
    Fixture que se aplica a todos los tests (autouse=True) y
    limpia por completo el logger raíz antes y después de cada uno.
    Esto asegura que basicConfig() siempre configure desde cero.
    """
    # Antes del test: retirar cualquier handler existente
    logging.root.handlers.clear()
    # Resetear el nivel para que basicConfig tenga efecto
    logging.root.setLevel(logging.NOTSET)
    yield
    # Después del test: limpiamos de nuevo
    logging.root.handlers.clear()
    logging.root.setLevel(logging.NOTSET)
