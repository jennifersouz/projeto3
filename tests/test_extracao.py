from __future__ import annotations

from pathlib import Path

import pymupdf
import pytest
from docx import Document

from motor.extracao import extrair_texto


def test_extrai_pdf(tmp_path: Path) -> None:
    caminho = tmp_path / "exemplo.pdf"
    documento = pymupdf.open()
    pagina = documento.new_page()
    pagina.insert_text((72, 72), "Ação de formação", fontsize=12)
    documento.save(caminho)
    documento.close()

    assert "Ação de formação" in extrair_texto(caminho)


def test_extrai_docx(tmp_path: Path) -> None:
    caminho = tmp_path / "exemplo.docx"
    documento = Document()
    documento.add_paragraph("Parecer jurídico sintético")
    documento.save(caminho)

    assert "Parecer jurídico sintético" in extrair_texto(caminho)


def test_formato_nao_suportado(tmp_path: Path) -> None:
    caminho = tmp_path / "exemplo.txt"
    caminho.write_text("texto", encoding="utf-8")

    with pytest.raises(ValueError):
        extrair_texto(caminho)


def test_ficheiro_inexistente(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        extrair_texto(tmp_path / "nao-existe.pdf")
