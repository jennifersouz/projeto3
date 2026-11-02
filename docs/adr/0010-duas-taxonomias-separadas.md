# 0010: Duas taxonomias separadas

- Status: Aceite
- Data: 2026-11-02

## Contexto

O projeto tem dois eixos diferentes. Um é a classe empresarial (`publico`, `uso_interno`, `confidencial`, `restrito`), com uma ordem de 0 a 3. O outro é a avaliação de impacto do PNCS, com três dimensões (`pessoas`, `estado`, `exposicao`) e níveis de 0 a 3.b. Misturar os dois num só ficheiro tornaria as regras difíceis de ler.

## Decisão

Manter `config/taxonomia_empresa.yaml` e `config/taxonomia_pncs.yaml` separados. A classe final usa a classe base do processo e as regras preliminares; as dimensões usam a pré-qualificação do processo e os efeitos do conteúdo.

## Consequências

- Há dois vocabulários para aprender e manter.
- As regras que ligam sinais a cada taxonomia estão em sítios diferentes.
- Alterar uma taxonomia não obriga a mexer na outra.
- O guia de anotação tem de explicar os dois eixos.
