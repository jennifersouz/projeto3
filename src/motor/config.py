from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


RAIZ_PROJETO = Path(__file__).resolve().parents[2]
DIRETORIA_CONFIG = RAIZ_PROJETO / "config"


def resolver_caminho(caminho: str | Path) -> Path:
    """Resolve um caminho relativo à raiz do projeto."""
    caminho = Path(caminho)
    if caminho.is_absolute():
        return caminho
    return RAIZ_PROJETO / caminho


def carregar_yaml(caminho: str | Path) -> Any:
    caminho = resolver_caminho(caminho)
    with caminho.open(encoding="utf-8") as ficheiro:
        return yaml.safe_load(ficheiro)


def carregar_processos() -> list[dict[str, Any]]:
    return carregar_yaml(DIRETORIA_CONFIG / "processos.yaml")


def carregar_taxonomia_empresa() -> dict[str, Any]:
    return carregar_yaml(DIRETORIA_CONFIG / "taxonomia_empresa.yaml")


def carregar_taxonomia_pncs() -> dict[str, Any]:
    return carregar_yaml(DIRETORIA_CONFIG / "taxonomia_pncs.yaml")


def carregar_config_corpus() -> dict[str, Any]:
    return carregar_yaml(DIRETORIA_CONFIG / "corpus.yaml")
