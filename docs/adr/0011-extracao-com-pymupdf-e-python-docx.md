# 0011: Extração com PyMuPDF e python-docx

- Status: Aceite
- Data: 2026-11-02

## Contexto

Os documentos do corpus são PDF e DOCX, e o motor precisa de texto simples para a futura classificação. São dois formatos com APIs diferentes.

## Decisão

Usar PyMuPDF para PDF e python-docx para DOCX. A função `motor/extracao.py:extrair_texto` escolhe o extrator pela extensão, devolve `FileNotFoundError` se o ficheiro não existir e `ValueError` para formatos não suportados.

## Consequências

- A extração cobre apenas `.pdf` e `.docx`.
- PDFs sem camada de texto (digitalizações) não são tratados por OCR.
- O teste de extração cria documentos mínimos e não depende de ficheiros externos.
