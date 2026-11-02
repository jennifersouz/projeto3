# ContextIQ

ContextIQ é um projeto em Python concebido para extrair, organizar e preparar o contexto de documentos PDF e DOCX para análise, indexação ou fluxos de trabalho com IA.

O repositório inclui a configuração do projeto, as dependências para trabalhar com documentos e o primeiro bloco de trabalho: um corpus sintético etiquetado para medir a qualidade da classificação.

## Funcionalidades

- Extração de texto de PDF com PyMuPDF e de DOCX com python-docx
- Taxonomias configuráveis em YAML: empresarial e PNCS
- Processos de negócio com pré-qualificação provisória das três dimensões
- Geração reprodutível de corpus sintético em PDF e DOCX
- Amostra de dupla anotação e cálculo do kappa de Cohen
- Divisão estratificada do corpus em treino e teste
- Configuração de projeto limpa para Python 3.13, com gestão de dependências via uv

## Estado do projeto

O projeto encontra-se numa fase inicial. Estão concluídos a extração de texto, a configuração das taxonomias e dos processos e a ferramenta de geração e anotação do corpus. A próxima etapa é o motor de sinais e o classificador baseline.

## Requisitos

- Python 3.13
- uv (recomendado para a gestão de dependências)

## Instalação

Clone o repositório e instale as dependências:

```bash
cd projeto3
uv sync
```

Todas as dependências estão declaradas no `pyproject.toml` e fixadas no `uv.lock`.

## Corpus sintético

O corpus é gerado localmente e fica em `dados/corpus/`, que não é versionado. Só são usados documentos sintéticos ou públicos.

Gerar o corpus (50 documentos por processo, num total de 300):

```bash
uv run python scripts/gerar_corpus.py --limpar
```

Saídas:

- `dados/corpus/documentos/` — documentos PDF e DOCX com nomes neutros;
- `dados/corpus/etiquetas.csv` — processo, dimensões, classe, justificação, split e hash;
- `dados/corpus/manifesto.json` — parâmetros, contagens e aviso da regra provisória.

Preparar a amostra de 50 documentos para dupla anotação:

```bash
uv run python scripts/preparar_amostra_anotacao.py --limpar
```

Cada anotador preenche `dados/anotacao/anotador_a.csv` ou `anotador_b.csv` de forma independente. O guia está em [`docs/guia_anotacao.md`](docs/guia_anotacao.md).

Calcular o kappa de Cohen:

```bash
uv run python scripts/calcular_kappa.py
```

O resultado fica em `dados/anotacao/kappa.json`. O mínimo aceite para avançar é 0,61 no kappa macro; abaixo disso, o guia de anotação deve ser revisto.

## Utilização

Extrair o texto de um documento PDF ou DOCX:

```bash
uv run python scripts/extrair_texto.py examples/0001100011.pdf
```

O corpus pode ser lido a partir das etiquetas:

```python
import csv
from pathlib import Path

with Path("dados/corpus/etiquetas.csv").open(encoding="utf-8", newline="") as ficheiro:
    documentos = list(csv.DictReader(ficheiro))

for documento in documentos:
    print(documento["id"], documento["processo"], documento["classe"])
```

## Estrutura do projeto

```text
projeto3/
├── .venv/                  # Ambiente virtual local
├── .gitignore
├── .python-version
├── config/                 # Taxonomias, processos e parâmetros do corpus
│   ├── taxonomia_empresa.yaml
│   ├── taxonomia_pncs.yaml
│   ├── processos.yaml
│   └── corpus.yaml
├── dados/                  # Corpus e anotações gerados localmente (ignorado)
├── docs/                   # Guia de anotação e enunciado
├── examples/               # Documento de exemplo
├── scripts/                # Comandos de linha de comandos
├── src/
│   └── motor/              # Código principal: configuração, extração, corpus, kappa
├── tests/                  # Testes com pytest
├── pyproject.toml          # Metadados do projeto e dependências
├── uv.lock                 # Ficheiro de bloqueio para instalações reprodutíveis
└── README.md               # Documentação do projeto
```

## Desenvolvimento

Para executar os testes:

```bash
uv run pytest
```

Para adicionar novas dependências:

```bash
uv add <nome-do-pacote>
```

## Dependências

As dependências atuais são:

- pymupdf
- python-docx
- faker
- pyyaml
- pytest (apenas para desenvolvimento)
