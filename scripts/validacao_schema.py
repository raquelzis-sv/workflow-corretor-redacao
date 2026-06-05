"""Validação de payloads contra JSON Schema."""

from __future__ import annotations

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PONTOS = ROOT_DIR / "schemas" / "pontos_interesse.json"


def validar_pontos_interesse(data: dict, schema_path: Path | None = None) -> tuple[bool, list[str]]:
    """
    Valida o JSON de pontos de interesse contra schemas/pontos_interesse.json.

    :return: (ok, lista de mensagens de erro)
    """
    path = schema_path or SCHEMA_PONTOS
    try:
        import jsonschema
    except ImportError:
        return _validar_minimo(data)

    with open(path, encoding="utf-8") as f:
        schema = json.load(f)

    erros: list[str] = []
    validator = jsonschema.Draft7Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
        loc = ".".join(str(p) for p in err.path) or "raiz"
        erros.append(f"{loc}: {err.message}")

    return len(erros) == 0, erros


def _validar_minimo(data: dict) -> tuple[bool, list[str]]:
    """Fallback sem dependência jsonschema."""
    erros = []
    if "pontos_interesse" not in data:
        erros.append("campo obrigatório ausente: pontos_interesse")
    elif not isinstance(data["pontos_interesse"], list):
        erros.append("pontos_interesse deve ser uma lista")
    return len(erros) == 0, erros
