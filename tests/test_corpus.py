from __future__ import annotations

import csv
from pathlib import Path

import pymupdf
import pytest
from docx import Document

from motor.config import carregar_config_corpus, carregar_processos
from motor.corpus import (
    CABECALHO_ETIQUETAS,
    dimensoes_base,
    gerar_corpus,
    hash_sha256,
)


ESCALA = {"S": 0, "M": 1, "G": 2}
CLASSES = {"publico", "uso_interno", "confidencial", "restrito"}
DIMENSOES = {"S", "M", "G"}


@pytest.fixture(scope="module")
def corpus_gerado(tmp_path_factory: pytest.TempPathFactory):
    destino = tmp_path_factory.mktemp("corpus")
    registos = gerar_corpus(destino=destino, por_processo=2, seed=1234)
    return destino, registos


def ler_etiquetas(destino: Path) -> list[dict[str, str]]:
    with (destino / "etiquetas.csv").open(encoding="utf-8", newline="") as ficheiro:
        return list(csv.DictReader(ficheiro))


def extrair_texto(registo: dict[str, str]) -> str:
    caminho = Path(registo["ficheiro"])
    if registo["formato"] == "pdf":
        with pymupdf.open(caminho) as documento:
            return "\n".join(pagina.get_text() for pagina in documento)
    documento = Document(caminho)
    return "\n".join(paragrafo.text for paragrafo in documento.paragraphs)


def sinais_do_registo(registo: dict[str, str]) -> set[str]:
    return {sinal for sinal in registo["sinais"].split(";") if sinal}


def test_gera_quantidade_esperada(corpus_gerado) -> None:
    destino, registos = corpus_gerado
    etiquetas = ler_etiquetas(destino)

    assert len(registos) == 12
    assert len(etiquetas) == 12
    assert list(etiquetas[0]) == CABECALHO_ETIQUETAS
    assert sum(1 for registo in registos if registo["formato"] == "pdf") == 6
    assert sum(1 for registo in registos if registo["formato"] == "docx") == 6
    assert {registo["processo"] for registo in registos} == {
        processo["id"] for processo in carregar_processos()
    }


def test_split_estratificado_por_processo(corpus_gerado) -> None:
    _, registos = corpus_gerado
    for processo in {registo["processo"] for registo in registos}:
        do_processo = [r for r in registos if r["processo"] == processo]
        assert sum(r["split"] == "treino" for r in do_processo) == 1
        assert sum(r["split"] == "teste" for r in do_processo) == 1


def test_etiquetas_validas_e_ficheiros_integridade(corpus_gerado) -> None:
    _, registos = corpus_gerado
    for registo in registos:
        assert registo["formato"] in {"pdf", "docx"}
        assert registo["pessoas"] in DIMENSOES
        assert registo["estado"] in DIMENSOES
        assert registo["exposicao"] in DIMENSOES
        assert registo["classe"] in CLASSES
        assert registo["split"] in {"treino", "teste"}
        assert registo["justificacao"]

        caminho = Path(registo["ficheiro"])
        assert caminho.is_file()
        assert hash_sha256(caminho) == registo["hash_sha256"]
        assert "DOCUMENTO SINTÉTICO" in extrair_texto(registo)


def test_dimensoes_nunca_abaixo_da_base_do_processo(corpus_gerado) -> None:
    _, registos = corpus_gerado
    config = carregar_config_corpus()
    processos = {processo["id"]: processo for processo in carregar_processos()}

    for registo in registos:
        base = dimensoes_base(processos[registo["processo"]], config)
        for dimensao in ("pessoas", "estado", "exposicao"):
            assert ESCALA[registo[dimensao]] >= ESCALA[base[dimensao]]


def test_regras_de_classe_sao_consistentes(corpus_gerado) -> None:
    _, registos = corpus_gerado
    for registo in registos:
        sinais = sinais_do_registo(registo)
        if registo["classe"] == "publico":
            assert "publicacao_autorizada" in sinais
            assert not sinais & {"iban", "dados_clinicos", "credenciais"}
        if "credenciais" in sinais:
            assert registo["classe"] == "restrito"


def test_geracao_e_reprodutivel(corpus_gerado, tmp_path: Path) -> None:
    _, registos = corpus_gerado
    outros = gerar_corpus(destino=tmp_path / "corpus", por_processo=2, seed=1234)

    def resumo(items):
        return [
            (
                item["id"],
                item["formato"],
                item["processo"],
                item["pessoas"],
                item["estado"],
                item["exposicao"],
                item["classe"],
                item["sinais"],
                item["justificacao"],
                item["split"],
            )
            for item in sorted(items, key=lambda item: item["id"])
        ]

    assert resumo(registos) == resumo(outros)


def test_recusa_regenerar_sem_limpar(tmp_path: Path) -> None:
    destino = tmp_path / "corpus"
    gerar_corpus(destino=destino, por_processo=1, seed=7)

    with pytest.raises(FileExistsError):
        gerar_corpus(destino=destino, por_processo=1, seed=7)

    registos = gerar_corpus(
        destino=destino, por_processo=1, seed=7, limpar=True
    )
    assert len(registos) == len(carregar_processos())


def test_recusa_por_processo_invalido(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        gerar_corpus(destino=tmp_path / "corpus", por_processo=0, seed=7)
