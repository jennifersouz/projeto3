from __future__ import annotations

import csv
from pathlib import Path

import pytest

from motor.anotacao import (
    CABECALHO_AMOSTRA,
    preparar_amostra_anotacao,
    selecionar_amostra,
)
from motor.corpus import gerar_corpus


def ler_csv(caminho: Path) -> list[dict[str, str]]:
    with caminho.open(encoding="utf-8", newline="") as ficheiro:
        return list(csv.DictReader(ficheiro))


def test_prepara_amostra_com_folhas_independentes(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    gerar_corpus(destino=corpus, por_processo=2, seed=11)

    destino = tmp_path / "anotacao"
    manifesto = preparar_amostra_anotacao(
        etiquetas=corpus / "etiquetas.csv",
        destino=destino,
        tamanho=6,
        seed=12,
    )

    assert manifesto["tamanho"] == 6
    assert sum(manifesto["processos"].values()) == 6
    assert all(quantidade == 1 for quantidade in manifesto["processos"].values())

    folha_a = ler_csv(destino / "anotador_a.csv")
    folha_b = ler_csv(destino / "anotador_b.csv")

    assert list(folha_a[0]) == CABECALHO_AMOSTRA
    assert len(folha_a) == len(folha_b) == 6
    assert [linha["id"] for linha in folha_a] == [linha["id"] for linha in folha_b]

    for linha in folha_a + folha_b:
        assert linha["ficheiro"]
        for campo in ("processo", "pessoas", "estado", "exposicao", "classe"):
            assert linha[campo] == ""


def test_recusa_substituir_anotacoes_sem_limpar(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    gerar_corpus(destino=corpus, por_processo=1, seed=21)

    destino = tmp_path / "anotacao"
    preparar_amostra_anotacao(
        etiquetas=corpus / "etiquetas.csv",
        destino=destino,
        tamanho=6,
        seed=22,
    )

    with pytest.raises(FileExistsError):
        preparar_amostra_anotacao(
            etiquetas=corpus / "etiquetas.csv",
            destino=destino,
            tamanho=6,
            seed=22,
        )

    manifesto = preparar_amostra_anotacao(
        etiquetas=corpus / "etiquetas.csv",
        destino=destino,
        tamanho=6,
        seed=22,
        limpar=True,
    )
    assert manifesto["tamanho"] == 6


def test_selecao_estratificada_prefere_um_por_processo(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    registos = gerar_corpus(destino=corpus, por_processo=2, seed=31)

    selecionados = selecionar_amostra(registos, tamanho=6, seed=32)
    assert len(selecionados) == 6
    assert len({registo["processo"] for registo in selecionados}) == 6


def test_amostra_maior_que_corpus_falha(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    registos = gerar_corpus(destino=corpus, por_processo=1, seed=41)

    with pytest.raises(ValueError):
        selecionar_amostra(registos, tamanho=len(registos) + 1, seed=42)
