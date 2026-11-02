import pytest

from motor.sinais import detetar_processo, detetar_sinais


def test_nif_valido_e_detetado():
    # 299861104 é um NIF estruturalmente válido (dígito de controlo correto)
    texto = "Identificação fiscal\nNIF: 299861104\n"
    deteccao = detetar_sinais(texto)
    assert "nif" in deteccao.sinais


def test_nif_invalido_e_ignorado():
    # 987654321 tem dígito de controlo 2 em vez de 1
    texto = "NIF: 987654321"
    deteccao = detetar_sinais(texto)
    assert "nif" not in deteccao.sinais


def test_iban_pt50_detetado_com_espacos():
    texto = "IBAN: PT50 0002 0123 1234 5678 9015 4\n"
    deteccao = detetar_sinais(texto)
    assert "iban" in deteccao.sinais


def test_credenciais_detetadas():
    texto = "Ação: credenciais de acesso sintéticas\npalavra-passe=DEMO-123456"
    deteccao = detetar_sinais(texto)
    assert "credenciais" in deteccao.sinais


def test_dados_clinicos_detetados():
    texto = "Diagnóstico: hipertensão arterial. Plano terapêutico prescrito."
    deteccao = detetar_sinais(texto)
    assert "dados_clinicos" in deteccao.sinais


def test_publicacao_autorizada_detetada():
    texto = "Documento aprovado para divulgação pública no portal institucional."
    deteccao = detetar_sinais(texto)
    assert "publicacao_autorizada" in deteccao.sinais


def test_sem_sinais_nao_deteta_nada():
    deteccao = detetar_sinais("Ata de reunião ordinária sem dados sensíveis.")
    assert deteccao.sinais == set()


def test_processo_identificado_por_lexico():
    texto = (
        "Proposta de Fornecedor\nObjeto: Aquisição de equipamento informático.\n"
        "Júri avaliou a qualidade técnica, o preço e o prazo de entrega.\n"
        "Procedimento de contratação pública."
    )
    processo, scores = detetar_processo(texto)
    assert processo == "aquisicao"
    assert scores["aquisicao"] >= 4


def test_processo_fallback_outro():
    processo, _ = detetar_processo("Documento com informação diversa.")
    assert processo == "outro"
