# 0004: As dimensões só sobem, nunca descem

- Status: Aceite
- Data: 2026-11-02

## Contexto

A pré-qualificação do processo é uma estimativa; o documento concreto pode mostrar mais risco (por exemplo, credenciais), mas não deve servir para "limpar" o risco herdado. Se o conteúdo pudesse descer uma dimensão, bastava um documento sem sinais para anular a criticidade do processo.

## Decisão

O conteúdo só pode aumentar a dimensão (`S` < `M` < `G`). O valor final nunca fica abaixo do valor herdado do processo. A regra está em `config/taxonomia_pncs.yaml` (`regra_conteudo`) e é aplicada em `motor/corpus.py:aplicar_efeitos_conteudo`.

## Consequências

- A regra é simples de testar e está coberta por `tests/test_corpus.py`.
- Em alguns casos o documento fica classificado acima do que o texto sugere, por herança do processo.
- Casos duvidosos continuam a ir para revisão humana.
