from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


RAIZ_PROJETO = Path(__file__).resolve().parents[2]
DIRETORIA_CONFIG = RAIZ_PROJETO / "config"
FICHEIRO_PROCESSOS = DIRETORIA_CONFIG / "processos.yaml"

SINAIS = frozenset(
    {
        "nif",
        "iban",
        "credenciais",
        "dados_clinicos",
        "publicacao_autorizada",
    }
)


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


def validar_config_processos(dados: Any) -> None:
    """Validar a estrutura de processos.yaml e falhar cedo com mensagem clara."""
    if not isinstance(dados, dict):
        raise ValueError("processos.yaml deve ser um mapa YAML")

    for chave in ("limiar_processo", "descricao_sinal", "processos"):
        if chave not in dados:
            raise ValueError(f"processos.yaml sem a chave obrigatória '{chave}'")

    limiar = dados["limiar_processo"]
    if isinstance(limiar, bool) or not isinstance(limiar, int) or limiar < 1:
        raise ValueError("limiar_processo deve ser um inteiro positivo")

    descricao_sinal = dados["descricao_sinal"]
    if not isinstance(descricao_sinal, dict):
        raise ValueError("descricao_sinal deve ser um mapa sinal -> descrição")

    desconhecidos = set(descricao_sinal) - SINAIS
    if desconhecidos:
        raise ValueError(
            f"descricao_sinal tem sinais desconhecidos: {sorted(desconhecidos)}"
        )
    faltam = SINAIS - set(descricao_sinal)
    if faltam:
        raise ValueError(f"descricao_sinal sem descrição para: {sorted(faltam)}")
    for sinal, texto in descricao_sinal.items():
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError(f"descricao_sinal['{sinal}'] deve ser texto não vazio")

    processos = dados["processos"]
    if not isinstance(processos, list) or not processos:
        raise ValueError("processos deve ser uma lista não vazia")

    ids: set[str] = set()
    for indice, processo in enumerate(processos):
        if not isinstance(processo, dict):
            raise ValueError(f"processos[{indice}] deve ser um mapa")
        processo_id = processo.get("id")
        if not isinstance(processo_id, str) or not processo_id.strip():
            raise ValueError(f"processos[{indice}] sem 'id' válido")
        if processo_id in ids:
            raise ValueError(f"id de processo duplicado: '{processo_id}'")
        ids.add(processo_id)

        nome = processo.get("nome")
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError(f"processo '{processo_id}' sem 'nome' válido")

        lexico = processo.get("lexico", [])
        if not isinstance(lexico, list):
            raise ValueError(f"lexico do processo '{processo_id}' deve ser uma lista")
        for entrada in lexico:
            if not isinstance(entrada, dict) or set(entrada) != {"padrao", "peso"}:
                raise ValueError(
                    f"cada entrada de lexico de '{processo_id}' deve ter "
                    "apenas 'padrao' e 'peso'"
                )
            padrao = entrada["padrao"]
            peso = entrada["peso"]
            if not isinstance(padrao, str) or not padrao.strip():
                raise ValueError(
                    f"lexico de '{processo_id}' tem um 'padrao' vazio ou inválido"
                )
            if isinstance(peso, bool) or not isinstance(peso, int) or peso < 1:
                raise ValueError(
                    f"lexico de '{processo_id}' tem peso inválido em '{padrao}'"
                )
            try:
                compilado = re.compile(padrao, re.IGNORECASE)
            except re.error as erro:
                raise ValueError(
                    f"lexico de '{processo_id}' tem padrão inválido "
                    f"'{padrao}': {erro}"
                ) from erro
            if compilado.fullmatch(""):
                raise ValueError(
                    f"lexico de '{processo_id}' tem padrão que casa com vazio: "
                    f"'{padrao}'"
                )

    if "outro" not in ids:
        raise ValueError("processos.yaml deve incluir o processo de fallback 'outro'")


@lru_cache(maxsize=None)
def _ler_config_processos_validada(caminho: str) -> dict[str, Any]:
    dados = carregar_yaml(caminho)
    validar_config_processos(dados)
    return dados


def carregar_config_processos(caminho: str | Path | None = None) -> dict[str, Any]:
    caminho_resolvido = resolver_caminho(caminho or FICHEIRO_PROCESSOS)
    return _ler_config_processos_validada(str(caminho_resolvido))


def carregar_processos(caminho: str | Path | None = None) -> list[dict[str, Any]]:
    return carregar_config_processos(caminho)["processos"]


@lru_cache(maxsize=None)
def _ler_config_sinais_validada(caminho: str) -> dict[str, Any]:
    dados = _ler_config_processos_validada(caminho)
    return {
        "limiar_processo": dados["limiar_processo"],
        "descricao_sinal": dict(dados["descricao_sinal"]),
        "lexico_processos": {
            processo["id"]: [
                (re.compile(entrada["padrao"], re.IGNORECASE), entrada["peso"])
                for entrada in processo.get("lexico", [])
            ]
            for processo in dados["processos"]
        },
    }


def carregar_config_sinais(caminho: str | Path | None = None) -> dict[str, Any]:
    caminho_resolvido = resolver_caminho(caminho or FICHEIRO_PROCESSOS)
    return _ler_config_sinais_validada(str(caminho_resolvido))


def carregar_taxonomia_empresa() -> dict[str, Any]:
    return carregar_yaml(DIRETORIA_CONFIG / "taxonomia_empresa.yaml")


def carregar_taxonomia_pncs() -> dict[str, Any]:
    return carregar_yaml(DIRETORIA_CONFIG / "taxonomia_pncs.yaml")


def carregar_config_corpus() -> dict[str, Any]:
    return carregar_yaml(DIRETORIA_CONFIG / "corpus.yaml")
