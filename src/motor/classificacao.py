"""Tradução de sinais e processo em classe, por taxonomia.

Um único cálculo de sinais (camada 1) alimenta qualquer taxonomia:
cada taxonomia só traduz (processo, dimensões, sinais) numa classe.
Trocar de taxonomia não obriga a reanalisar o documento.

A regra PNCS é provisória (hipótese didática do guia) e não o referencial
oficial do CNCS e da ARTE.
"""

from __future__ import annotations

from typing import Any

from motor.config import (
    carregar_config_corpus,
    carregar_config_sinais,
    carregar_processos,
    carregar_taxonomia_empresa,
    carregar_taxonomia_pncs,
)
from motor.corpus import (
    ORDEM_CLASSE,
    aplicar_efeitos_conteudo,
    dimensoes_base,
)
from motor.sinais import sinais_do_documento


def nivel_pncs(dimensoes: dict[str, str], processo: dict[str, Any]) -> str:
    """Regra provisória: S/M/G → 0, 1, 2, 3.a (3.b só com controlo nacional)."""
    n_g = sum(1 for valor in dimensoes.values() if valor == "G")
    n_m = sum(1 for valor in dimensoes.values() if valor == "M")

    if n_g == 0 and n_m == 0:
        nivel = "0"
    elif n_g == 0:
        nivel = "1"
    elif n_g == 1:
        nivel = "2"
    else:
        nivel = "3.a"

    if nivel == "3.a" and processo.get("controlo_nacional", False):
        nivel = "3.b"

    return nivel


def classe_empresa(
    processo_id: str,
    sinais: set[str],
    config: dict[str, Any],
    empresa: dict[str, Any],
) -> str:
    """Classe base do processo + regras preliminares da taxonomia empresarial."""
    classe = config.get("classe_base_por_processo", {}).get(
        processo_id, "uso_interno"
    )
    regras = {regra["sinal"]: regra for regra in empresa.get("regras_preliminares", [])}
    impeditivos = sinais & {"iban", "dados_clinicos", "credenciais"}

    sinal_para_regra = {
        "iban": "iban_em_contexto_nao_publico",
        "dados_clinicos": "dados_clinicos_identificaveis",
        "credenciais": "credenciais_de_acesso_ou_segredos_de_sistema_critico",
        "nif": "nif_ou_identificadores_pessoais",
        "publicacao_autorizada": "divulgacao_publica_autorizada",
    }

    for sinal in sorted(sinais):
        regra = regras.get(sinal_para_regra.get(sinal))
        if regra is None:
            continue
        efeito = regra.get("efeito")

        if efeito == "classe_minima":
            minima = regra["classe"]
            if ORDEM_CLASSE[minima] > ORDEM_CLASSE[classe]:
                classe = minima
        elif (
            efeito == "permite_publico_se_ausencia_de_sinais_sensiveis"
            and sinal == "publicacao_autorizada"
            and not impeditivos
            and ORDEM_CLASSE[classe] <= ORDEM_CLASSE["uso_interno"]
        ):
            classe = "publico"

    return classe


def justificacao(
    processo_id: str,
    processo_nome: str,
    sinais: set[str],
    deteccao_evidencia: dict[str, list[str]],
    dimensoes: dict[str, str],
    classe: str,
    taxonomia: str,
    codigos_clav: list[dict[str, Any]] | None = None,
    descricao_sinal: dict[str, str] | None = None,
) -> str:
    """Frase curta que refere sinais concretos, não genérica."""
    descricao_sinal = descricao_sinal or {}
    partes = [
        f"{descricao_sinal[s]}" for s in sorted(sinais) if s in descricao_sinal
    ]
    inicio = f"Contém {', '.join(partes)}" if partes else "Sem sinais sensíveis detetados"

    clav = ""
    if codigos_clav:
        codigo = codigos_clav[0]["codigo"]
        clav = f" Processo mapeado em CLAV {codigo}."

    pncs = ""
    if taxonomia == "pncs":
        resumo = "/".join(
            f"{dim}={dimensoes[dim]}" for dim in ("pessoas", "estado", "exposicao")
        )
        pncs = f" Dimensões: {resumo} (regra provisória)."

    return (
        f"{inicio}; processo de {processo_nome}.{clav}{pncs} "
        f"Classe {classe} pela taxonomia '{taxonomia}'."
    )


def classificar_texto(
    texto: str,
    taxonomia: str = "empresa",
) -> dict[str, Any]:
    """Caminho completo da camada 1 por cima de um texto já extraído.

    Devolve o bloco de sinais uma única vez; a taxonomia só traduz.
    """
    config = carregar_config_corpus()
    config_sinais = carregar_config_sinais()
    processos = {p["id"]: p for p in carregar_processos()}
    empresa = carregar_taxonomia_empresa()

    deteccao = sinais_do_documento(texto, config)
    processo_id = deteccao.processo
    processo = processos.get(processo_id, {"id": "outro", "nome": "Outro"})

    dimensoes = aplicar_efeitos_conteudo(
        dimensoes_base(processo, config),
        deteccao.sinais,
        config,
    )

    nivel_pncs_str = nivel_pncs(dimensoes, processo)
    pncs = carregar_taxonomia_pncs()
    nome_nivel = next(
        n["nome"]
        for n in pncs["niveis_oficiais"]
        if n["codigo"] == nivel_pncs_str
    )

    if taxonomia == "pncs":
        classe = nivel_pncs_str
        nome_classe = nome_nivel
    else:
        classe = classe_empresa(processo_id, deteccao.sinais, config, empresa)
        nome_classe = next(
            c["nome"] for c in empresa["classes"] if c["id"] == classe
        )

    return {
        "processo": processo_id,
        "processo_nome": processo["nome"],
        "sinais": sorted(deteccao.sinais),
        "evidencia": deteccao.evidencia,
        "scores_processo": deteccao.scores_processo,
        "pessoas": dimensoes["pessoas"],
        "estado": dimensoes["estado"],
        "exposicao": dimensoes["exposicao"],
        "nivel_pncs": {
            "codigo": nivel_pncs_str,
            "nome": nome_nivel,
        },
        "taxonomia": taxonomia,
        "classe": classe,
        "nome_classe": nome_classe,
        "justificacao": justificacao(
            processo_id,
            processo["nome"],
            deteccao.sinais,
            deteccao.evidencia,
            dimensoes,
            classe,
            taxonomia,
            processo.get("codigos_clav"),
            config_sinais["descricao_sinal"],
        ),
        "camada_decisora": "regras",
        "confianca": None,
        "aviso": (
            "Regra provisória; não é o referencial oficial do CNCS e da ARTE. "
            "Confirmação por revisão humana recomendada."
        ),
    }
