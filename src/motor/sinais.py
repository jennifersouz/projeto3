"""Camada 1: deteção de sinais e indícios de processo por regras e léxico.

Aplica padrões (regex) e palavras-chave sobre o texto extraído de um
documento para confirmar sinais de sensibilidade e propor o processo de
negócio. Não usa rede nem modelos treinados; cada deteção é justificável
com o excerto onde apareceu.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from motor.config import SINAIS, carregar_config_sinais

# --- Padrões de sinais -------------------------------------------------------

_PADRAO_NIF = re.compile(
    r"(?:NIF|N\.?\s?I\.?\s?F\.?)\b[^:\-\n]{0,30}?[:\-]\s*([1-9][0-9]{8})",
    re.IGNORECASE,
)

_PADRAO_IBAN = re.compile(
    r"PT50(?:[\s\-]?\d{4}){5}[\s\-]?\d(?![\s\-]*\d)"
)

_PADAO_CREDENCIAIS = re.compile(
    r"(?i)\b(?:"
    r"palavra[\s\-]*passe|password|credenciais de acesso|token de acesso|"
    r"chave de acesso|segredo de sistema|utilizador\s*[:=]|palavra[\s\-]*passe\s*[:=]"
    r")"
)

_PADRAO_DADOS_CLINICOS = re.compile(
    r"(?i)\b(?:"
    r"diagn[oó]stico|n[uú]mero de utente|plano terap[eê]utico|prescri[çc][ãa]o m[eé]dica|"
    r"exames realizados|relat[oó]rio cl[ií]nico|resultado laboratorial|consulta de especialidade|"
    r"utente|processo cl[ií]nico"
    r")\b"
)

_PADRAO_PUBLICACAO = re.compile(
    r"(?i)\b(?:"
    r"divulga[çc][ãa]o p[uú]blica|aprovado para divulga[çc][ãa]o|publicado no portal|"
    r"portal institucional|portal da transpar[eê]ncia|pode ser publicado"
    r")\b"
)

@dataclass
class Deteccao:
    """Resultado da camada 1 sobre um documento."""

    sinais: set[str] = field(default_factory=set)
    evidencia: dict[str, list[str]] = field(default_factory=dict)
    processo: str = "outro"
    scores_processo: dict[str, int] = field(default_factory=dict)

    def notar_sinal(self, sinal: str) -> None:
        if sinal in SINAIS:
            self.sinais.add(sinal)


def _nif_valido(candidato: str) -> bool:
    if len(candidato) != 9:
        return False
    base, digito = candidato[:8], int(candidato[8])
    soma = sum(int(d) * peso for d, peso in zip(base, range(9, 1, -1)))
    resto = soma % 11
    return digito == (0 if resto < 2 else 11 - resto)


def _padrao_nif() -> re.Pattern[str]:
    return _PADRAO_NIF


def detetar_sinais(texto: str) -> Deteccao:
    """Confirmar sinais de sensibilidade com padrões diretos e validar o NIF."""
    deteccao = Deteccao()

    for encontrado in _padrao_nif().finditer(texto):
        if _nif_valido(encontrado.group(1)):
            deteccao.notar_sinal("nif")
            deteccao.evidencia.setdefault("nif", []).append(
                f"NIF validado: {encontrado.group(1)}"
            )

    for encontrado in _PADRAO_IBAN.finditer(texto):
        deteccao.notar_sinal("iban")
        deteccao.evidencia.setdefault("iban", []).append(
            f"IBAN PT50 detetado: {encontrado.group(0).strip()[:40]}"
        )

    for encontrado in _PADAO_CREDENCIAIS.finditer(texto):
        deteccao.notar_sinal("credenciais")
        deteccao.evidencia.setdefault("credenciais", []).append(
            f"Marcador de credenciais: {encontrado.group(0).strip()[:40]}"
        )

    for encontrado in _PADRAO_DADOS_CLINICOS.finditer(texto):
        deteccao.notar_sinal("dados_clinicos")
        deteccao.evidencia.setdefault("dados_clinicos", []).append(
            f"Marcador clínico: {encontrado.group(0)}"
        )

    for encontrado in _PADRAO_PUBLICACAO.finditer(texto):
        deteccao.notar_sinal("publicacao_autorizada")
        deteccao.evidencia.setdefault("publicacao_autorizada", []).append(
            f"Marcador de publicação autorizada: {encontrado.group(0)}"
        )

    return deteccao


def _ordenar_deteccao(
    scores: dict[str, int],
) -> dict[str, int]:
    return dict(sorted(scores.items(), key=lambda par: (-par[1], par[0])))


def detetar_processo(
    texto: str,
    config_sinais: dict[str, Any] | None = None,
) -> tuple[str, dict[str, int]]:
    """Propor o processo de negócio com léxico e limiar vindos do YAML."""
    config_sinais = config_sinais or carregar_config_sinais()
    lexico = config_sinais["lexico_processos"]
    limiar = config_sinais["limiar_processo"]

    texto_normalizado = texto.lower()
    scores = _ordenar_deteccao(
        {
            processo: sum(
                peso for padrao, peso in padroes if padrao.search(texto_normalizado)
            )
            for processo, padroes in lexico.items()
        }
    )
    melhor = max(scores, key=scores.get) if scores else "outro"
    if scores.get(melhor, 0) < limiar:
        return "outro", _ordenar_deteccao(scores)
    return melhor, scores


def sinais_do_documento(
    texto: str, config: dict[str, Any]
) -> Deteccao:
    """Detectar sinais e filtrar pelos permitidos por processo (config)."""
    deteccao = detetar_sinais(texto)
    processo, scores = detetar_processo(texto)
    deteccao.processo = processo
    deteccao.scores_processo = scores
    permitidos = config.get("sinais_permitidos", {}).get(
        processo,
        ["nif", "iban"],
    )
    deteccao.sinais &= set(permitidos)
    for sinal in list(deteccao.evidencia):
        if sinal not in deteccao.sinais:
            deteccao.evidencia.pop(sinal, None)
    return deteccao
