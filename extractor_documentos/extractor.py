
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document


def extrair_pdf(caminho):
    """Extrai o texto de um ficheiro PDF."""
    textos = []

    with fitz.open(caminho) as documento:
        for pagina in documento:
            texto = pagina.get_text("text")
            textos.append(texto)

    return "\n\n".join(textos)


def extrair_docx(caminho):
    """Extrai o texto dos parágrafos de um DOCX."""
    documento = Document(caminho)

    paragrafos = [
        paragrafo.text
        for paragrafo in documento.paragraphs
    ]

    return "\n".join(paragrafos)


def extrair_texto(caminho):
    """Identifica o formato e extrai o texto."""
    caminho = Path(caminho)

    if not caminho.is_file():
        raise FileNotFoundError(
            f"Ficheiro não encontrado: {caminho}"
        )

    formato = caminho.suffix.lower()

    if formato == ".pdf":
        return extrair_pdf(caminho)

    elif formato == ".docx":
        return extrair_docx(caminho)

    else:
        raise ValueError(
            f"Formato não suportado: {formato}"
        )


if __name__ == "__main__":
    caminho = "documentos/0001100011.pdf"

    try:
        if caminho.lower().endswith(".pdf"):
            texto_extraido = extrair_pdf(caminho)

        elif caminho.lower().endswith(".docx"):
            texto_extraido = extrair_docx(caminho)

        else:
            raise ValueError("Formato não suportado.")

        print("Texto extraído:")
        print(texto_extraido)

    except FileNotFoundError:
        print("Erro: Ficheiro não encontrado.")

    except Exception as erro:
        print(f"Erro ao processar documento: {erro}")