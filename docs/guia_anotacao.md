# Guia de anotação do corpus sintético

Este guia serve para anotar os documentos do corpus do ContextIQ de forma
consistente. A anotação é uma **regra provisória da equipa**, não o referencial
oficial do CNCS e da ARTE. Só podem ser usados documentos **sintéticos ou
públicos**; nunca documentos reais, confidenciais ou pessoais.

## Fluxo de trabalho

1. Gerar o corpus:

   ```bash
   uv run python scripts/gerar_corpus.py --limpar
   ```

2. Preparar a amostra de calibração:

   ```bash
   uv run python scripts/preparar_amostra_anotacao.py --limpar
   ```

3. Cada anotador preenche a sua folha, **sem consultar a folha do outro** nem
   as etiquetas de referência:
   - `dados/anotacao/anotador_a.csv`
   - `dados/anotacao/anotador_b.csv`

4. Calcular o kappa de Cohen:

   ```bash
   uv run python scripts/calcular_kappa.py
   ```

5. Se o kappa macro for inferior a **0,61**, rever este guia, esclarecer os
   exemplos e repetir a amostra antes de anotar o resto do corpus.

## Campos da folha

| Campo | Valores | Notas |
| --- | --- | --- |
| `id` | `doc-0001` | Não alterar. |
| `ficheiro` | caminho relativo | Não alterar. |
| `processo` | `aquisicao`, `juridico`, `investigacao_desenvolvimento`, `saude`, `gestao_administrativa`, `outro` | Escolher um. |
| `pessoas` | `S`, `M` ou `G` | Dimensão "Pessoas e vida humana". |
| `estado` | `S`, `M` ou `G` | Dimensão "Estabilidade do Estado". |
| `exposicao` | `S`, `M` ou `G` | Dimensão "Exposição de dados". |
| `classe` | `publico`, `uso_interno`, `confidencial`, `restrito` | Taxonomia empresarial. |

Usar maiúsculas em `S`, `M`, `G` e os identificadores em minúsculas na classe.

## Processos de negócio

| ID | Processo | Exemplos de conteúdo |
| --- | --- | --- |
| `aquisicao` | Aquisição | Propostas de fornecedores, avaliação de propostas, contratos. |
| `juridico` | Jurídico | Pareceres, notas jurídicas, pedidos de interpretação. |
| `investigacao_desenvolvimento` | Investigação e Desenvolvimento | Relatórios de I&D, protótipos, planos de investigação. |
| `saude` | Saúde | Relatórios clínicos, resultados laboratoriais, imagiologia. |
| `gestao_administrativa` | Gestão Administrativa | Atas, convocatórias, recomendações. |
| `outro` | Outro / não identificado | Documentos sem processo identificável com confiança. |

## Dimensões de impacto

- **Pessoas e vida humana**: o comprometimento pode ameaçar a segurança ou a
  vida de pessoas?
- **Estabilidade do Estado**: pode afetar a continuidade ou a estabilidade das
  funções do Estado ou dos serviços públicos?
- **Exposição de dados**: que dano causa a divulgação indevida da informação?

Escala:

| Código | Nome | Critério prático |
| --- | --- | --- |
| `S` | Sem Impacto | Não há consequência relevante identificável. |
| `M` | Impacto Moderado | Consequência limitada, reversível e circunscrita. |
| `G` | Impacto Significativo | Consequência grave, difícil de reverter ou com alcance elevado. |

## Classes empresariais

| Classe | Significado | Exemplos |
| --- | --- | --- |
| `publico` | Informação aprovada para divulgação pública, sem sinais impeditivos. | Aviso de concurso publicado; ata publicada sem dados sensíveis. |
| `uso_interno` | Informação operacional não destinada ao público. | Convocatória interna; nota de serviço corrente. |
| `confidencial` | Informação pessoal, financeira, clínica ou comercial de acesso restrito. | Recibo com NIF/IBAN; relatório clínico identificável; proposta antes da adjudicação. |
| `restrito` | Informação crítica ou segredo de elevada sensibilidade. | Credenciais de acesso; plano de segurança de sistema crítico. |

## Regras de decisão

1. Classificar o **processo de negócio**, não apenas o documento. Um documento
   banal pode pertencer a um processo crítico.
2. As dimensões herdam a pré-qualificação do processo. O conteúdo concreto só
   pode **subir** uma dimensão, nunca descê-la.
3. Sinais no conteúdo:
   - `NIF`: sobe a exposição um nível, mas por si só não torna o documento
     Confidencial; exige contexto.
   - `IBAN`: sobe a exposição um nível e impõe pelo menos **Confidencial**.
   - `dados clínicos identificáveis`: Pessoas e Exposição passam a **G** e
     impõem pelo menos **Confidencial**.
   - `credenciais de acesso`: Estado e Exposição passam a **G** e impõem
     **Restrito**.
   - `publicação autorizada`: permite **Público** apenas se não existirem IBAN,
     dados clínicos ou credenciais. NIF sozinho não impede.
4. Sem sinais sensíveis, usar a classe base:
   - `saude` → `confidencial`;
   - restantes processos → `uso_interno`.
5. Em caso de dúvida, baixa confiança ou conteúdo ambíguo, **sinalizar revisão
   humana**. Não inventar etiquetas.
6. Errar para baixo é pior do que errar para cima. Um documento Restrito
   classificado como Público é o erro mais grave.

## Interpretação do kappa

O kappa mede a concordância entre os dois anotadores, corrigindo o acaso:

| Kappa | Interpretação |
| --- | --- |
| `< 0` | Pior que o acaso |
| `0,00–0,20` | Fraca |
| `0,21–0,40` | Razoável |
| `0,41–0,60` | Moderada |
| `0,61–0,80` | Substancial |
| `0,81–1,00` | Quase perfeita |

O mínimo aceite para avançar é **0,61** no kappa macro. O resultado fica em
`dados/anotacao/kappa.json`, com o valor por campo e a concordância global.

## Avisos

- A regra de níveis e classes deste guia é **provisória** e não substitui o
  referencial técnico oficial do CNCS e da ARTE. Confirmar a publicação em
  `digital.gov.pt` antes de qualquer uso real.
- O inventário e as etiquetas também são sensíveis: indicam onde estão os
  documentos mais críticos. Não versionar dados reais.
- Os documentos do corpus têm a marca "DOCUMENTO SINTÉTICO - SEM VALOR LEGAL"
  e não podem ser usados como documentos oficiais.
