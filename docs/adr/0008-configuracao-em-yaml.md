# 0008: Configuração em YAML

- Status: Aceite
- Data: 2026-11-02

## Contexto

As taxonomias, a lista de processos e os parâmetros do corpus mudam com frequência e não faz sentido estar a alterar Python para cada ajuste. Também queremos que as regras fiquem num sítio legível e versionável.

## Decisão

Guardar tudo o que é configurável em `config/`: `processos.yaml`, `taxonomia_empresa.yaml`, `taxonomia_pncs.yaml` e `corpus.yaml`. O carregamento é feito por `motor/config.py` com `yaml.safe_load` e os caminhos relativos são resolvidos a partir da raiz do projeto.

## Consequências

- As regras e os parâmetros podem ser alterados sem tocar no motor.
- Não há validação de schema: um YAML mal formado ou um campo em falta só dá erro quando é usado.
- Os testes e a geração dependem da estrutura destes ficheiros.
- Os YAML são a fonte de verdade; os dados gerados em `dados/` não.
