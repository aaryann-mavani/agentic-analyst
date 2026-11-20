"""Question routing: the first answer type (by PRIORITY, then module name) whose PATTERN matches the Question."""
from __future__ import annotations

import importlib
import pkgutil
import re
from types import ModuleType

from . import answer_types


def answer_type_modules() -> list[ModuleType]:
    mods = [importlib.import_module(f"{answer_types.__name__}.{m.name}") for m in pkgutil.iter_modules(answer_types.__path__)]
    return sorted(mods, key=lambda m: (getattr(m, "PRIORITY", 100), m.__name__))


def route(question: str) -> ModuleType | None:
    for mod in answer_type_modules():
        if re.search(mod.PATTERN, question, re.IGNORECASE):
            return mod
    return None
