from typing import Generator

from src.core.config import Settings, get_settings

def settings_dependency() -> Generator[Settings, None, None]:
    yield get_settings()
