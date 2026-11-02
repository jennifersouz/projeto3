from __future__ import annotations

from pathlib import Path

import pymupdf
from docx import Document


def extrair_pdf(caminho: str | Path) -> str:
    """Extrai o texto de um ficheiro PDF."""
    textos: list[str] = []

    with pymupdf.open(caminho) as documento:
        for pagina in documento:
            textos.append(pagina.get_text("text"))

    return "\n\n".join(textos)


def extrair_docx(caminho: str | Path) -> str:
    """Extrai o texto dos parágrafos de um DOCX."""
    documento = Document(caminho)
    return "\n".join(paragrafo.text for paragrafo in documento.paragraphs)


def extrair_texto(caminho: str | Path) -> str:
    """Identifica o formato e extrai o texto."""
    caminho = Path(caminho)

    if not caminho.is_file():
        raise FileNotFoundError(f"Ficheiro não encontrado: {caminho}")

    formato = caminho.suffix.lower()

    if formato == ".pdf":
        return extrair_pdf(caminho)
    if formato == ".docx":
        return extrair_docx(caminho)
    raise ValueError(f"Formato não suportado: {formato}")
