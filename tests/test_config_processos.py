import copy

import pytest
import yaml

from motor.config import (
    SINAIS,
    carregar_config_processos,
    carregar_config_sinais,
    carregar_processos,
    validar_config_processos,
)
from motor.sinais import detetar_processo


def _config_valida() -> dict:
    return {
        "limiar_processo": 4,
        "descricao_sinal": {sinal: f"descrição de {sinal}" for sinal in SINAIS},
        "processos": [
            {
                "id": "aquisicao",
                "nome": "Aquisição",
                "lexico": [{"padrao": "proposta de fornecedor", "peso": 3}],
            },
            {"id": "outro", "nome": "Outro", "lexico": []},
        ],
    }


def _escrever(tmp_path, dados: dict):
    caminho = tmp_path / "processos.yaml"
    caminho.write_text(
        yaml.safe_dump(dados, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return caminho


def test_config_valida_passa():
    validar_config_processos(_config_valida())


@pytest.mark.parametrize("chave", ["limiar_processo", "descricao_sinal", "processos"])
def test_config_sem_chave_obrigatoria_falha(chave):
    dados = _config_valida()
    del dados[chave]
    with pytest.raises(ValueError, match=chave):
        validar_config_processos(dados)


def test_limiar_tem_de_ser_inteiro_positivo():
    dados = _config_valida()
    dados["limiar_processo"] = 0
    with pytest.raises(ValueError, match="limiar_processo"):
        validar_config_processos(dados)


def test_descricao_tem_de_cobrir_todos_os_sinais():
    dados = _config_valida()
    del dados["descricao_sinal"]["nif"]
    with pytest.raises(ValueError, match="nif"):
        validar_config_processos(dados)


def test_descricao_com_sinal_desconhecido_falha():
    dados = _config_valida()
    dados["descricao_sinal"]["sinal_inventado"] = "x"
    with pytest.raises(ValueError, match="sinal_inventado"):
        validar_config_processos(dados)


def test_ids_de_processo_nao_se_repetem():
    dados = _config_valida()
    dados["processos"].append(copy.deepcopy(dados["processos"][0]))
    with pytest.raises(ValueError, match="duplicado"):
        validar_config_processos(dados)


def test_expressao_regular_invalida_falha():
    dados = _config_valida()
    dados["processos"][0]["lexico"][0]["padrao"] = "(["
    with pytest.raises(ValueError, match="padrão inválido"):
        validar_config_processos(dados)


def test_padrao_que_casa_com_vazio_falha():
    dados = _config_valida()
    dados["processos"][0]["lexico"][0]["padrao"] = "a*"
    with pytest.raises(ValueError, match="vazio"):
        validar_config_processos(dados)


def test_peso_invalido_falha():
    dados = _config_valida()
    dados["processos"][0]["lexico"][0]["peso"] = 0
    with pytest.raises(ValueError, match="peso inválido"):
        validar_config_processos(dados)


def test_fallback_outro_e_obrigatorio():
    dados = _config_valida()
    dados["processos"] = dados["processos"][:1]
    with pytest.raises(ValueError, match="outro"):
        validar_config_processos(dados)


def test_lexico_e_limiar_vem_do_yaml(tmp_path):
    dados = _config_valida()
    dados["limiar_processo"] = 5
    dados["processos"][0]["lexico"] = [
        {"padrao": "palavra-chave-unica", "peso": 3}
    ]
    caminho = _escrever(tmp_path, dados)

    config = carregar_config_sinais(caminho)
    processo, scores = detetar_processo(
        "texto com palavra-chave-unica", config_sinais=config
    )
    assert processo == "outro"
    assert scores["aquisicao"] == 3


def test_baixar_limiar_no_yaml_muda_a_decisao(tmp_path):
    dados = _config_valida()
    dados["limiar_processo"] = 3
    dados["processos"][0]["lexico"] = [
        {"padrao": "palavra-chave-unica", "peso": 3}
    ]
    caminho = _escrever(tmp_path, dados)

    config = carregar_config_sinais(caminho)
    processo, scores = detetar_processo(
        "texto com palavra-chave-unica", config_sinais=config
    )
    assert processo == "aquisicao"
    assert scores["aquisicao"] == 3


def test_carregar_processos_devolve_lista_do_yaml(tmp_path):
    caminho = _escrever(tmp_path, _config_valida())
    processos = carregar_processos(caminho)
    assert [p["id"] for p in processos] == ["aquisicao", "outro"]


def test_config_por_omissao_tem_descricoes_e_lexico():
    config = carregar_config_sinais()
    assert config["limiar_processo"] == 4
    assert set(config["descricao_sinal"]) == SINAIS
    assert config["lexico_processos"]["aquisicao"]
    assert config["lexico_processos"]["outro"] == []


def test_config_processos_por_omissao_tem_ids_esperados():
    ids = [processo["id"] for processo in carregar_config_processos()["processos"]]
    assert ids == [
        "aquisicao",
        "juridico",
        "investigacao_desenvolvimento",
        "saude",
        "gestao_administrativa",
        "outro",
    ]
