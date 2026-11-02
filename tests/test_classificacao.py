from typing import Any

from motor.classificacao import classificar_texto, nivel_pncs
from motor.config import carregar_config_corpus, carregar_processos


def _texto_aquisicao_com_nif() -> str:
    return (
        "Proposta de Fornecedor\nObjeto: Aquisição de equipamento informático.\n"
        "Informe-se: procedimento de contratação pública.\nJúri avaliou a proposta.\n"
        "NIF do contato: 299861104\n"
    )


def test_classificar_empresa_classe_confidencial_com_ibano():
    texto = (
        "Proposta de Fornecedor\nContrato de aquisição de bens.\n"
        "Procedimento de contratação pública.\nIBAN: PT50 0002 0123 1234 5678 9015 4\n"
    )
    resultado = classificar_texto(texto, "empresa")
    assert resultado["processo"] == "aquisicao"
    assert resultado["classe"] == "confidencial"
    assert resultado["camada_decisora"] == "regras"
    assert "Confidencial" in resultado["nome_classe"]


def test_classificar_ambas_as_taxonomias_sem_reanalisar():
    texto = _texto_aquisicao_com_nif()
    empresa = classificar_texto(texto, "empresa")
    pncs = classificar_texto(texto, "pncs")
    assert empresa["sinais"] == pncs["sinais"]
    assert empresa["processo"] == pncs["processo"]
    assert empresa["classe"] != pncs["classe"]
    assert pncs["classe"] in {"0", "1", "2", "3.a", "3.b"}


def test_niveis_pncs_tabela_provisoria():
    processo: dict[str, Any] = {"id": "x", "controlo_nacional": False}
    assert nivel_pncs({"pessoas": "S", "estado": "S", "exposicao": "S"}, processo) == "0"
    assert nivel_pncs({"pessoas": "S", "estado": "M", "exposicao": "S"}, processo) == "1"
    assert nivel_pncs({"pessoas": "S", "estado": "M", "exposicao": "G"}, processo) == "2"
    assert nivel_pncs({"pessoas": "G", "estado": "M", "exposicao": "G"}, processo) == "3.a"
    nivel_3b = nivel_pncs(
        {"pessoas": "G", "estado": "G", "exposicao": "G"},
        {"id": "y", "controlo_nacional": True},
    )
    assert nivel_3b == "3.b"


def test_saude_herde_dimensao_e_sobe_nunca_desce():
    texto_saude = (
        "Relatório Clínico\nUtente: Maria Silva\nNúmero de utente: 123456789\n"
        "Diagnóstico: hipertensão arterial.\nExames realizados: hemograma.\n"
    )
    resultado = classificar_texto(texto_saude, "pncs")
    # pré-qualificação do processo Saúde: pessoas=G, exposicao=G; conteúdo não desce
    assert resultado["pessoas"] == "G"
    assert resultado["exposicao"] == "G"
    assert resultado["nivel_pncs"]["codigo"] == "3.a"


def test_justificacao_nao_e_generica():
    resultado = classificar_texto(_texto_aquisicao_com_nif(), "empresa")
    assert "NIF" in resultado["justificacao"]
    assert resultado["processo_nome"] in resultado["justificacao"]


def test_config_e_processos_carregados():
    config = carregar_config_corpus()
    processos = carregar_processos()
    assert len(processos) == 6
    assert "classe_base_por_processo" in config
