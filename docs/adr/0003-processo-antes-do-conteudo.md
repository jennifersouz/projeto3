# 0003: Classificar o processo antes do conteúdo

- Status: Aceite
- Data: 2026-11-02

## Contexto

A mesma frase pode ser inofensiva num processo e crítica noutro. O guia de anotação diz explicitamente para classificar o processo de negócio e não apenas o documento; a taxonomia PNCS tem a mesma regra em `regra_pre_qualificacao`. Sem essa ordem, um documento banal de um processo crítico podia sair como `uso_interno` só porque o texto não tinha sinais óbvios.

## Decisão

A classificação começa pelo processo (`aquisicao`, `juridico`, `investigacao_desenvolvimento`, `saude`, `gestao_administrativa`, `outro`). As dimensões PNCS herdam a pré-qualificação do processo; o conteúdo do documento só entra depois, para ajustar.

## Consequências

- Cada processo tem de ter uma pré-qualificação provisória definida em `config/processos.yaml` (o `outro` não tem).
- O classificador futuro tem de identificar o processo antes de avaliar as dimensões.
- Um erro na identificação do processo propaga-se para o resto da classificação.
