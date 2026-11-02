# 0007: Split estratificado por processo e geração com seed

- Status: Aceite
- Data: 2026-11-02

## Contexto

O corpus tem 50 documentos por processo. Um split aleatório simples podia deixar um processo com pouca ou nenhuma representação no teste. Ao mesmo tempo, queremos conseguir repetir exatamente o mesmo corpus e o mesmo split.

## Decisão

Dividir o corpus em treino e teste por processo, com proporção de teste de 0,2 e pelo menos um documento de teste por processo. Usar seeds fixas: 4900 para o corpus, 4901 para a amostra e `seed + 1` para o split. O Faker é inicializado com `seed_instance`. Os scripts aceitam `--seed`, `--por-processo` e `--limpar`.

## Consequências

- Com os valores por omissão, ficam 240 documentos em treino e 60 em teste.
- Mudar a seed muda o corpus e o split; para regenerar é preciso `--limpar`.
- O split é verificável em `tests/test_corpus.py`.
- A estratificação por processo não garante equilíbrio por classe.
