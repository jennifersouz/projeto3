# 0002: Corpus sintético em vez de documentos reais

- Status: Aceite
- Data: 2026-11-02

## Contexto

Para treinar e avaliar um classificador precisamos de documentos etiquetados. Usar documentos reais traria dados pessoais e informação potencialmente confidencial para dentro de um trabalho académico e para o repositório, o que não é aceitável. Também não seria possível partilhar o corpus com outra pessoa.

## Decisão

Gerar os documentos localmente com o Faker (`pt_PT`) e escrevê-los em PDF e DOCX. Cada documento leva a marca "DOCUMENTO SINTÉTICO - SEM VALOR LEGAL" e uma instituição fictícia. O corpus fica em `dados/corpus/`, que está no `.gitignore`. Só entram documentos sintéticos ou públicos; nunca reais.

## Consequências

- O corpus pode ser apagado, partilhado e regenerado sem problemas legais.
- A geração é reprodutível com a mesma seed, mas os documentos não representam a distribuição real de um arquivo.
- Os resultados do futuro classificador não podem ser extrapolados automaticamente para documentos reais.
- O gerador tem de cobrir os formatos e os processos que queremos testar: 300 documentos, 50 por processo, metade PDF e metade DOCX.
