# 0001: Python 3.13 e uv

- Status: Aceite
- Data: 2026-11-02

## Contexto

O projeto arrancou de raiz e precisava de um ambiente fácil de reproduzir noutra máquina. As dependências principais (PyMuPDF, python-docx, Faker, PyYAML) e o pytest têm de ficar em versões conhecidas, senão os testes e o corpus deixam de ser reproduzíveis. O `pyproject.toml` exige `>=3.13,<3.14` e o `.python-version` está em `3.13.17`.

## Decisão

Usar Python 3.13 e `uv` para gerir o ambiente e as dependências. O `uv.lock` fica no repositório e o projeto não é publicado como pacote (`[tool.uv] package = false`).

## Consequências

- A instalação é `uv sync` e os comandos correm com `uv run`.
- As versões ficam fixas no `uv.lock`.
- Quem não usar `uv` tem de instalar as dependências à mão e perde a garantia de reprodução.
- O projeto é tratado como aplicação, não como biblioteca.
