# 0012: Categoria de fallback `outro`

- Status: Aceite
- Data: 2026-11-02

## Contexto

Há documentos que não encaixam em nenhum processo com confiança suficiente. Forçá-los numa categoria real daria uma etiqueta errada e esconderia o problema.

## Decisão

Criar o processo `outro` como fallback, sem pré-qualificação (`pre_qualificacao_provisoria: null`) e com a indicação de que exige revisão humana.

## Consequências

- Nenhum documento fica sem etiqueta.
- A classe base do `outro` é `uso_interno`, porque não há pré-qualificação.
- A categoria não deve ser usada como destino normal; serve para triagem.
