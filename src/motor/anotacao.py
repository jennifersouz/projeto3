from __future__ import annotations

import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from motor.config import carregar_config_corpus, resolver_caminho
from motor.kappa import CAMPOS_ANOTACAO


CABECALHO_AMOSTRA = ["id", "ficheiro", *CAMPOS_ANOTACAO]


def ler_etiquetas(caminho: str | Path) -> list[dict[str, str]]:
    caminho = resolver_caminho(caminho)
    with caminho.open(encoding="utf-8", newline="") as ficheiro:
        registos = list(csv.DictReader(ficheiro))
    if not registos:
        raise ValueError(f"{caminho} não contém documentos")
    return registos


def selecionar_amostra(
    registos: list[dict[str, str]], tamanho: int, seed: int
) -> list[dict[str, str]]:
    if tamanho < 1:
        raise ValueError("O tamanho da amostra tem de ser pelo menos 1")
    if tamanho > len(registos):
        raise ValueError(
            f"A amostra pedida ({tamanho}) é maior do que o corpus "
            f"({len(registos)})"
        )

    rng = random.Random(seed)
    grupos: dict[str, list[dict[str, str]]] = defaultdict(list)
    for registo in registos:
        grupos[registo["processo"]].append(registo)

    processos = sorted(grupos)
    base, resto = divmod(tamanho, len(processos))
    selecionados: list[dict[str, str]] = []

    for indice, processo in enumerate(processos):
        pedido = base + (1 if indice < resto else 0)
        candidatos = list(grupos[processo])
        rng.shuffle(candidatos)
        selecionados.extend(candidatos[:pedido])

    if len(selecionados) < tamanho:
        ids = {registo["id"] for registo in selecionados}
        restantes = [registo for registo in registos if registo["id"] not in ids]
        rng.shuffle(restantes)
        selecionados.extend(restantes[: tamanho - len(selecionados)])

    return sorted(selecionados, key=lambda registo: registo["id"])


def escrever_folha_anotacao(
    caminho: Path, registos: list[dict[str, str]]
) -> None:
    with caminho.open("w", encoding="utf-8", newline="") as ficheiro:
        escritor = csv.DictWriter(ficheiro, fieldnames=CABECALHO_AMOSTRA)
        escritor.writeheader()
        for registo in registos:
            escritor.writerow(
                {
                    "id": registo["id"],
                    "ficheiro": registo["ficheiro"],
                    **{campo: "" for campo in CAMPOS_ANOTACAO},
                }
            )


def preparar_amostra_anotacao(
    etiquetas: str | Path | None = None,
    destino: str | Path | None = None,
    tamanho: int | None = None,
    seed: int | None = None,
    limpar: bool = False,
) -> dict[str, Any]:
    config = carregar_config_corpus()
    config_amostra = config.get("amostra_anotacao", {})

    etiquetas = resolver_caminho(
        etiquetas or Path(config["diretoria_saida"]) / "etiquetas.csv"
    )
    destino = resolver_caminho(
        destino or config_amostra.get("diretoria_saida", "dados/anotacao")
    )
    tamanho = int(
        tamanho if tamanho is not None else config_amostra.get("tamanho", 50)
    )
    seed = int(
        seed
        if seed is not None
        else config_amostra.get("seed", config["seed"] + 1)
    )

    destino.mkdir(parents=True, exist_ok=True)
    ficheiros = [
        destino / "anotador_a.csv",
        destino / "anotador_b.csv",
        destino / "manifesto.json",
    ]
    existentes = [caminho for caminho in ficheiros if caminho.exists()]
    if existentes and not limpar:
        nomes = ", ".join(caminho.name for caminho in existentes)
        raise FileExistsError(
            f"Já existem ficheiros de anotação ({nomes}); use limpar=True "
            "ou a opção --limpar para os substituir."
        )

    registos = ler_etiquetas(etiquetas)
    selecionados = selecionar_amostra(registos, tamanho, seed)

    escrever_folha_anotacao(ficheiros[0], selecionados)
    escrever_folha_anotacao(ficheiros[1], selecionados)

    manifesto = {
        "tamanho": len(selecionados),
        "seed": seed,
        "ids": [registo["id"] for registo in selecionados],
        "processos": {
            processo: sum(
                1 for registo in selecionados if registo["processo"] == processo
            )
            for processo in sorted({registo["processo"] for registo in selecionados})
        },
        "instrucoes": (
            "Cada anotador preenche a sua folha de forma independente, sem ver "
            "a folha do outro nem as etiquetas de referência. Seguir "
            "docs/guia_anotacao.md e calcular o kappa antes de anotar o resto."
        ),
        "aviso": (
            "Amostra de calibração. As etiquetas de referência não são "
            "mostradas aos anotadores."
        ),
    }
    with (destino / "manifesto.json").open("w", encoding="utf-8") as ficheiro:
        json.dump(manifesto, ficheiro, ensure_ascii=False, indent=2)

    return manifesto
