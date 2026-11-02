# 0009: CSV e JSON em vez de base de dados

- Status: Aceite
- Data: 2026-11-02

## Contexto

O volume é pequeno: 300 documentos no corpus, 50 na amostra de anotação e um resultado de kappa. As folhas de anotação têm de ser preenchidas à mão, por isso têm de ser fáceis de abrir e editar. Também não há necessidade de consultas concorrentes nem de transações.

## Decisão

Usar CSV para os dados tabulares (`etiquetas.csv`, `anotador_a.csv`, `anotador_b.csv`) e JSON para os manifestos e o resultado do kappa. Não usar base de dados.

## Consequências

- Os ficheiros abrem em qualquer editor ou no Excel e são fáceis de inspecionar.
- Não há integridade referencial imposta pela base de dados; as regras são validadas no código e nos testes.
- O modelo não escala bem para muitos milhares de documentos ou para escrita concorrente.
- Tudo o que está em `dados/` é regenerável e fica fora do Git.
