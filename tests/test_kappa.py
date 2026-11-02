from __future__ import annotations

import pytest

from motor.kappa import (
    cohen_kappa,
    comparar_anotadores,
    interpretar_kappa,
    validar_anotacoes,
)


def test_kappa_concordancia_perfeita() -> None:
    assert cohen_kappa(["S", "M", "G"], ["S", "M", "G"]) == 1.0


def test_kappa_exemplo_conhecido() -> None:
    assert cohen_kappa([0, 0, 1, 1], [0, 0, 0, 1]) == pytest.approx(0.5)


def test_kappa_etiqueta_unica_em_ambos() -> None:
    assert cohen_kappa(["S", "S"], ["S", "S"]) == 1.0


def test_kappa_listas_com_tamanhos_diferentes() -> None:
    with pytest.raises(ValueError):
        cohen_kappa(["S"], ["S", "M"])


def test_kappa_sem_itens() -> None:
    with pytest.raises(ValueError):
        cohen_kappa([], [])


def test_interpretar_kappa() -> None:
    assert interpretar_kappa(-0.1) == "pior que o acaso"
    assert interpretar_kappa(0.1) == "fraca"
    assert interpretar_kappa(0.3) == "razoável"
    assert interpretar_kappa(0.5) == "moderada"
    assert interpretar_kappa(0.7) == "substancial"
    assert interpretar_kappa(0.9) == "quase perfeita"


def _anotacao(processo: str = "saude") -> dict[str, str]:
    return {
        "processo": processo,
        "pessoas": "G",
        "estado": "S",
        "exposicao": "G",
        "classe": "confidencial",
    }


def test_comparar_anotadores() -> None:
    a = {"doc-0001": _anotacao(), "doc-0002": _anotacao("juridico")}
    b = {"doc-0001": _anotacao(), "doc-0002": _anotacao("juridico")}
    resultado = comparar_anotadores(a, b)
    assert resultado["n"] == 2
    assert resultado["kappa_conjunto"] == 1.0
    assert resultado["kappa_macro"] == 1.0
    assert set(resultado["campos"]) == {
        "processo",
        "pessoas",
        "estado",
        "exposicao",
        "classe",
    }


def test_comparar_anotadores_com_ids_diferentes() -> None:
    a = {"doc-0001": _anotacao()}
    b = {"doc-0002": _anotacao()}
    with pytest.raises(ValueError):
        comparar_anotadores(a, b)


def test_validar_anotacoes_detecta_campos_vazios() -> None:
    anotacao = _anotacao()
    anotacao["classe"] = ""
    with pytest.raises(ValueError):
        validar_anotacoes({"doc-0001": anotacao}, "anotador_a")


def test_validar_anotacoes_detecta_valores_invalidos() -> None:
    anotacao = _anotacao()
    anotacao["processo"] = "desconhecido"
    with pytest.raises(ValueError):
        validar_anotacoes({"doc-0001": anotacao}, "anotador_a")

    anotacao = _anotacao()
    anotacao["pessoas"] = "X"
    with pytest.raises(ValueError):
        validar_anotacoes({"doc-0001": anotacao}, "anotador_a")

    anotacao = _anotacao()
    anotacao["classe"] = "secreto"
    with pytest.raises(ValueError):
        validar_anotacoes({"doc-0001": anotacao}, "anotador_a")
