# 0006: Dupla anotação e kappa como critério de qualidade

- Status: Aceite
- Data: 2026-11-02

## Contexto

Antes de anotar o corpus todo, é preciso perceber se duas pessoas interpretam o guia da mesma forma. Sem isso, as etiquetas de referência podem estar a medir a interpretação de uma pessoa e não a regra. O kappa de Cohen corrige a concordância que aconteceria por acaso.

## Decisão

Retirar uma amostra de 50 documentos, dar a cada anotador uma folha independente (`anotador_a.csv` e `anotador_b.csv`) e calcular o kappa por campo e o kappa macro. O mínimo para avançar é 0,61. Abaixo disso, o guia é revisto e a amostra repetida antes de anotar o resto.

## Consequências

- Há trabalho manual antes de se poder avançar para o classificador.
- Os anotadores não podem ver as etiquetas de referência nem a folha um do outro.
- O resultado fica em `dados/anotacao/kappa.json`, com `aprovado` a refletir o limiar.
- O kappa macro é a média dos cinco campos (`processo`, `pessoas`, `estado`, `exposicao`, `classe`).
