from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from motor.config import carregar_processos, resolver_caminho


CAMPOS_ANOTACAO = ["processo", "pessoas", "estado", "exposicao", "classe"]
CAMPOS_ORDINAIS = {"pessoas", "estado", "exposicao", "classe"}


def cohen_kappa(a: Iterable[str], b: Iterable[str]) -> float:
    a = list(a)
    b = list(b)
    if len(a) != len(b):
        raise ValueError("As duas anotações têm de ter o mesmo número de itens")
    if not a:
        raise ValueError("Não é possível calcular kappa sem itens")

    n = len(a)
    acordo_observado = sum(x == y for x, y in zip(a, b)) / n
    distribuicao_a = Counter(a)
    distribuicao_b = Counter(b)
    etiquetas = set(distribuicao_a) | set(distribuicao_b)
    acordo_esperado = sum(
        (distribuicao_a[etiqueta] / n) * (distribuicao_b[etiqueta] / n)
        for etiqueta in etiquetas
    )

    if acordo_esperado >= 1:
        return 1.0 if acordo_observado >= 1 else 0.0
    return (acordo_observado - acordo_esperado) / (1 - acordo_esperado)


def interpretar_kappa(valor: float) -> str:
    if valor < 0:
        return "pior que o acaso"
    if valor <= 0.20:
        return "fraca"
    if valor <= 0.40:
        return "razoável"
    if valor <= 0.60:
        return "moderada"
    if valor <= 0.80:
        return "substancial"
    return "quase perfeita"


def ler_anotacoes(caminho: str | Path) -> dict[str, dict[str, str]]:
    caminho = resolver_caminho(caminho)
    with caminho.open(encoding="utf-8", newline="") as ficheiro:
        leitor = csv.DictReader(ficheiro)
        if not leitor.fieldnames or "id" not in leitor.fieldnames:
            raise ValueError(f"{caminho} não tem a coluna obrigatória 'id'")
        faltantes = [campo for campo in CAMPOS_ANOTACAO if campo not in leitor.fieldnames]
        if faltantes:
            raise ValueError(
                f"{caminho} não tem as colunas: {', '.join(faltantes)}"
            )
        registos: dict[str, dict[str, str]] = {}
        for linha in leitor:
            doc_id = (linha.get("id") or "").strip()
            if not doc_id:
                raise ValueError(f"{caminho} contém uma linha sem id")
            if doc_id in registos:
                raise ValueError(f"{caminho} contém o id repetido {doc_id}")
            registos[doc_id] = {
                campo: (linha.get(campo) or "").strip()
                for campo in CAMPOS_ANOTACAO
            }
    if not registos:
        raise ValueError(f"{caminho} não contém anotações")
    return registos


def validar_anotacoes(
    anotacoes: dict[str, dict[str, str]], nome: str
) -> None:
    vazios = [
        f"{doc_id}:{campo}"
        for doc_id, registo in anotacoes.items()
        for campo in CAMPOS_ANOTACAO
        if not registo[campo]
    ]
    if vazios:
        raise ValueError(
            f"{nome} tem campos por preencher: {', '.join(vazios[:10])}"
        )

    processos_validos = {
        processo["id"] for processo in carregar_processos()
    }
    for doc_id, registo in anotacoes.items():
        if registo["processo"] not in processos_validos:
            raise ValueError(
                f"{nome}: {doc_id}/processo tem valor inválido "
                f"{registo['processo']!r}"
            )
        for campo in ("pessoas", "estado", "exposicao"):
            if registo[campo] not in {"S", "M", "G"}:
                raise ValueError(
                    f"{nome}: {doc_id}/{campo} tem valor inválido "
                    f"{registo[campo]!r}; use S, M ou G"
                )
        if registo["classe"] not in {
            "publico",
            "uso_interno",
            "confidencial",
            "restrito",
        }:
            raise ValueError(
                f"{nome}: {doc_id}/classe tem valor inválido "
                f"{registo['classe']!r}"
            )


def comparar_anotadores(
    anotador_a: dict[str, dict[str, str]],
    anotador_b: dict[str, dict[str, str]],
) -> dict[str, Any]:
    ids_a = set(anotador_a)
    ids_b = set(anotador_b)
    if ids_a != ids_b:
        apenas_a = sorted(ids_a - ids_b)
        apenas_b = sorted(ids_b - ids_a)
        raise ValueError(
            "Os anotadores não têm os mesmos documentos; "
            f"apenas em A: {apenas_a[:10]}; apenas em B: {apenas_b[:10]}"
        )

    ids = sorted(ids_a)
    campos: dict[str, Any] = {}
    for campo in CAMPOS_ANOTACAO:
        valores_a = [anotador_a[doc_id][campo] for doc_id in ids]
        valores_b = [anotador_b[doc_id][campo] for doc_id in ids]
        acordo = sum(x == y for x, y in zip(valores_a, valores_b)) / len(ids)
        kappa = cohen_kappa(valores_a, valores_b)
        campos[campo] = {
            "n": len(ids),
            "acordo_observado": round(acordo, 4),
            "kappa": round(kappa, 4),
            "forca": interpretar_kappa(kappa),
            "ordinal": campo in CAMPOS_ORDINAIS,
        }

    tuplos_a = [
        tuple(anotador_a[doc_id][campo] for campo in CAMPOS_ANOTACAO)
        for doc_id in ids
    ]
    tuplos_b = [
        tuple(anotador_b[doc_id][campo] for campo in CAMPOS_ANOTACAO)
        for doc_id in ids
    ]
    kappa_conjunto = cohen_kappa(tuplos_a, tuplos_b)
    kappa_macro = sum(campos[campo]["kappa"] for campo in CAMPOS_ANOTACAO) / len(
        CAMPOS_ANOTACAO
    )

    return {
        "n": len(ids),
        "campos": campos,
        "kappa_conjunto": round(kappa_conjunto, 4),
        "forca_conjunto": interpretar_kappa(kappa_conjunto),
        "kappa_macro": round(kappa_macro, 4),
        "forca_macro": interpretar_kappa(kappa_macro),
    }
