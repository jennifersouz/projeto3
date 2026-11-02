from __future__ import annotations

import csv
import hashlib
import json
import random
import shutil
import textwrap
from collections import defaultdict
from pathlib import Path
from typing import Any

import pymupdf
from docx import Document
from faker import Faker

from motor.config import (
    RAIZ_PROJETO,
    DIRETORIA_CONFIG,
    carregar_config_corpus,
    carregar_processos,
    carregar_taxonomia_empresa,
    resolver_caminho,
)


ESCALA = {"S": 0, "M": 1, "G": 2}
ESCALA_INV = {0: "S", 1: "M", 2: "G"}
ORDEM_CLASSE = {"publico": 0, "uso_interno": 1, "confidencial": 2, "restrito": 3}

CABECALHO_ETIQUETAS = [
    "id",
    "ficheiro",
    "formato",
    "processo",
    "pessoas",
    "estado",
    "exposicao",
    "classe",
    "sinais",
    "justificacao",
    "split",
    "hash_sha256",
]

SINAL_PARA_REGRA = {
    "iban": "iban_em_contexto_nao_publico",
    "dados_clinicos": "dados_clinicos_identificaveis",
    "credenciais": "credenciais_de_acesso_ou_segredos_de_sistema_critico",
    "nif": "nif_ou_identificadores_pessoais",
    "publicacao_autorizada": "divulgacao_publica_autorizada",
}

INSTITUICOES = {
    "aquisicao": "Serviço de Compras da Câmara Fictícia de Vale Verde",
    "juridico": "Direção Jurídica da Entidade Fictícia Atlântico",
    "investigacao_desenvolvimento": "Instituto Fictício de Investigação Aplicada",
    "saude": "Hospital Fictício de Santa Luzia",
    "gestao_administrativa": "Secretaria-Geral da Entidade Fictícia Atlântico",
    "outro": "Arquivo Geral da Entidade Fictícia Atlântico",
}

ORDEM_JUSTIFICACAO = (
    ("credenciais", "credenciais de acesso sintéticas"),
    ("dados_clinicos", "dados clínicos identificáveis"),
    ("iban", "IBAN"),
    ("nif", "NIF"),
    ("publicacao_autorizada", "publicação autorizada"),
)

ASSUNTOS = {
    "aquisicao": [
        "Aquisição de equipamento informático",
        "Contratação de serviços de manutenção",
        "Fornecimento de material de escritório",
        "Prestação de serviços de limpeza",
        "Aquisição de licenças de software",
    ],
    "juridico": [
        "Interpretação de norma sobre contratação pública",
        "Parecer sobre proteção de dados pessoais",
        "Análise de minuta de contrato",
        "Questão jurídica sobre recursos humanos",
        "Aplicação do regime legal de arquivo",
    ],
    "investigacao_desenvolvimento": [
        "Desenvolvimento de protótipo industrial",
        "Investigação aplicada em materiais sustentáveis",
        "Plano de inovação tecnológica",
        "Estudo de viabilidade técnica",
        "Desenvolvimento experimental de sensor",
    ],
    "gestao_administrativa": [
        "Reunião ordinária do órgão executivo",
        "Reunião de coordenação operacional",
        "Convocatória do conselho consultivo",
        "Apreciação do plano anual de atividades",
        "Acompanhamento de deliberações anteriores",
    ],
    "outro": [
        "Informação diversa recebida pelos serviços",
        "Documento sem enquadramento identificado",
        "Nota interna de carácter geral",
        "Comunicação de serviço",
        "Elemento para triagem documental",
    ],
    "saude": [
        "Dor torácica e falta de ar",
        "Consulta de seguimento de hipertensão",
        "Avaliação de análises clínicas",
        "Dor lombar persistente",
        "Revisão de medicação crónica",
    ],
}

FRASES = {
    "aquisicao": [
        "A proposta foi apresentada no âmbito do procedimento de contratação pública.",
        "O júri avaliou a qualidade técnica, o preço e o prazo de entrega.",
        "O fornecedor deve cumprir as obrigações contratuais e de faturação.",
        "O valor adjudicado inclui os impostos legalmente aplicáveis.",
        "A documentação financeira foi conferida pelos serviços de contabilidade.",
    ],
    "juridico": [
        "O parecer analisa a interpretação da norma jurídica aplicável ao caso.",
        "A jurisprudência relevante foi considerada na fundamentação.",
        "O processo contém informação reservada que exige acesso restrito.",
        "A conclusão jurídica deve ser validada pelo dirigente competente.",
        "O pedido de parecer foi instruído com os elementos essenciais.",
    ],
    "investigacao_desenvolvimento": [
        "O projeto de investigação aplicada decorre no âmbito do consórcio.",
        "A metodologia prevê a realização de ensaios e prototipagem.",
        "Os resultados preliminares serão validados em ambiente controlado.",
        "O parceiro industrial acompanha o desenvolvimento experimental.",
        "A propriedade intelectual resultante deve ser avaliada.",
    ],
    "saude": [
        "O utente foi observado em consulta de especialidade.",
        "O diagnóstico teve por base a avaliação clínica e os exames realizados.",
        "O plano terapêutico inclui prescrição médica e reavaliação.",
        "Os dados clínicos são pessoais e exigem confidencialidade.",
        "O processo clínico deve ser conservado pelo período legal aplicável.",
    ],
    "gestao_administrativa": [
        "A reunião decorreu nas instalações da entidade, com a presença dos membros convocados.",
        "A ordem de trabalhos foi aprovada por unanimidade.",
        "As deliberações constam da ata e serão comunicadas aos serviços competentes.",
        "A ata deve ser arquivada no arquivo corrente da entidade.",
        "A documentação de suporte foi distribuída aos participantes.",
    ],
    "outro": [
        "O documento reúne informação diversa recebida pelos serviços.",
        "O conteúdo foi recebido pelos serviços e aguarda triagem.",
        "A entidade deve confirmar o enquadramento antes do arquivo definitivo.",
        "A informação disponível é reduzida e exige confirmação documental.",
        "A informação deve ser tratada de acordo com as normas internas.",
    ],
}


def paragrafo(rng: random.Random, processo_id: str, n: int) -> str:
    frases = FRASES.get(processo_id, FRASES["outro"])
    escolhidas = rng.sample(frases, min(n, len(frases)))
    if n > len(frases):
        escolhidas.extend(rng.choice(frases) for _ in range(n - len(frases)))
    return " ".join(escolhidas)


def gerar_nif(rng: random.Random) -> str:
    base = str(rng.choice([1, 2, 3, 5, 6, 7, 8, 9]))
    base += "".join(str(rng.randint(0, 9)) for _ in range(7))
    soma = sum(int(digito) * peso for digito, peso in zip(base, range(9, 1, -1)))
    resto = soma % 11
    check = 0 if resto < 2 else 11 - resto
    return base + str(check)


def formatar_iban(iban: str) -> str:
    return " ".join(iban[i : i + 4] for i in range(0, len(iban), 4))


def dados_identificacao(
    fake: Faker, rng: random.Random, sinais: set[str]
) -> list[str]:
    linhas = [
        f"Nome: {fake.name()}",
        f"Endereço: {fake.address().replace(chr(10), ', ')}",
        f"Contacto: {fake.phone_number()}",
    ]
    if "nif" in sinais:
        linhas.append(f"NIF: {gerar_nif(rng)}")
    if "iban" in sinais:
        linhas.append(f"IBAN: {formatar_iban(fake.iban())}")
    if "credenciais" in sinais:
        linhas.append(
            "Credenciais de acesso (sintéticas, sem validade): "
            f"utilizador=treino_{rng.randint(1000, 9999)}; "
            f"palavra-passe=DEMO-{rng.randint(100000, 999999)}"
        )
    return linhas


def documento_aquisicao(
    fake: Faker, rng: random.Random, sinais: set[str]
) -> tuple[str, list[str]]:
    titulo = rng.choice(
        [
            "Proposta de Fornecedor",
            "Relatório de Avaliação de Propostas",
            "Contrato de Aquisição de Bens e Serviços",
        ]
    )
    corpo = [
        f"Fornecedor: {fake.company()}",
        f"Objeto: {rng.choice(ASSUNTOS['aquisicao'])}.",
        f"Valor estimado: {rng.randint(1000, 250000)} EUR",
        f"Prazo de execução: {rng.randint(30, 365)} dias",
    ]
    corpo.extend(dados_identificacao(fake, rng, sinais))
    corpo.extend(
        [
            f"Descrição da proposta: {paragrafo(rng, 'aquisicao', 4)}",
            "Critérios de avaliação: preço, qualidade técnica e prazo de entrega.",
            "Conclusão do júri: a proposta reúne as condições exigidas no procedimento.",
        ]
    )
    return titulo, corpo


def documento_juridico(
    fake: Faker, rng: random.Random, sinais: set[str]
) -> tuple[str, list[str]]:
    titulo = rng.choice(
        ["Parecer Jurídico", "Nota Jurídica Interna", "Pedido de Interpretação Normativa"]
    )
    corpo = [
        f"Assunto: {rng.choice(ASSUNTOS['juridico'])}.",
        "Enquadramento: análise da norma aplicável e da jurisprudência relevante.",
        f"Análise: {paragrafo(rng, 'juridico', 5)}",
        "Conclusão: o parecer é favorável, com as reservas indicadas.",
    ]
    corpo.extend(dados_identificacao(fake, rng, sinais))
    return titulo, corpo


def documento_investigacao(
    fake: Faker, rng: random.Random, sinais: set[str]
) -> tuple[str, list[str]]:
    titulo = rng.choice(
        [
            "Relatório de Investigação Aplicada",
            "Memória Descritiva de Protótipo",
            "Plano de Investigação",
        ]
    )
    corpo = [
        f"Projeto: {rng.choice(ASSUNTOS['investigacao_desenvolvimento'])}.",
        f"Parceiro industrial: {fake.company()}",
        f"Objetivo: {rng.choice(FRASES['investigacao_desenvolvimento'])}",
        f"Metodologia: {paragrafo(rng, 'investigacao_desenvolvimento', 3)}",
        f"Resultados preliminares: {paragrafo(rng, 'investigacao_desenvolvimento', 3)}",
    ]
    corpo.extend(dados_identificacao(fake, rng, sinais))
    return titulo, corpo


def documento_saude(
    fake: Faker, rng: random.Random, sinais: set[str]
) -> tuple[str, list[str]]:
    titulo = rng.choice(
        ["Relatório Clínico", "Resultado Laboratorial", "Relatório Imagiológico"]
    )
    corpo = [
        f"Utente: {fake.name()}",
        f"Idade: {rng.randint(18, 90)} anos",
        f"Número de utente: {rng.randint(100000000, 999999999)}",
        f"Data de admissão: {fake.date_between(start_date='-2y', end_date='today').strftime('%d/%m/%Y')}",
    ]
    if "nif" in sinais:
        corpo.append(f"NIF: {gerar_nif(rng)}")
    corpo.extend(
        [
            f"Motivo de consulta: {rng.choice(ASSUNTOS['saude'])}.",
            "Diagnóstico: "
            + rng.choice(
                [
                    "hipertensão arterial",
                    "diabetes tipo 2",
                    "infeção respiratória",
                    "lombalgia crónica",
                    "anemia ferropénica",
                ]
            )
            + ".",
            "Exames realizados: hemograma, glicemia e imagiologia.",
            "Plano terapêutico: prescrição médica e reavaliação em 30 dias.",
            f"Observações clínicas: {paragrafo(rng, 'saude', 2)}",
            f"Médico responsável: {fake.name()}",
        ]
    )
    return titulo, corpo


def documento_gestao(
    fake: Faker, rng: random.Random, sinais: set[str]
) -> tuple[str, list[str]]:
    titulo = rng.choice(
        ["Ata de Reunião", "Convocatória de Reunião", "Recomendação de Órgão Consultivo"]
    )
    participantes = "; ".join(fake.name() for _ in range(rng.randint(3, 6)))
    corpo = [
        f"Reunião: {rng.choice(ASSUNTOS['gestao_administrativa'])}.",
        f"Data e local: {fake.date_between(start_date='-2y', end_date='today').strftime('%d/%m/%Y')}, instalações da entidade.",
        f"Participantes: {participantes}",
        f"Ordem de trabalhos: {paragrafo(rng, 'gestao_administrativa', 2)}",
        f"Deliberações: {paragrafo(rng, 'gestao_administrativa', 4)}",
    ]
    if "nif" in sinais:
        corpo.append(f"NIF do relator: {gerar_nif(rng)}")
    return titulo, corpo


def documento_outro(
    fake: Faker, rng: random.Random, sinais: set[str]
) -> tuple[str, list[str]]:
    titulo = rng.choice(["Memorando Interno", "Documento Diverso", "Nota de Serviço"])
    corpo = [
        f"Assunto: {rng.choice(ASSUNTOS['outro'])}.",
        f"Conteúdo: {paragrafo(rng, 'outro', 6)}",
    ]
    corpo.extend(dados_identificacao(fake, rng, sinais))
    return titulo, corpo


GERADORES = {
    "aquisicao": documento_aquisicao,
    "juridico": documento_juridico,
    "investigacao_desenvolvimento": documento_investigacao,
    "saude": documento_saude,
    "gestao_administrativa": documento_gestao,
    "outro": documento_outro,
}


def cabecalho_documento(
    processo_id: str,
    fake: Faker,
    rng: random.Random,
    sinais: set[str],
) -> list[str]:
    data = fake.date_between(start_date="-2y", end_date="today")
    linhas = [
        "DOCUMENTO SINTÉTICO - SEM VALOR LEGAL",
        f"Instituição fictícia: {INSTITUICOES.get(processo_id, 'Entidade Fictícia')}",
        f"Referência: REF-{rng.randint(10000, 99999)}/{data.year}",
        f"Data: {data.strftime('%d/%m/%Y')}",
    ]
    if "publicacao_autorizada" in sinais:
        linhas.append(
            "Documento aprovado para divulgação pública no portal institucional."
        )
    return linhas


def compor_documento(
    processo: dict[str, Any],
    fake: Faker,
    rng: random.Random,
    sinais: set[str],
) -> tuple[str, list[str]]:
    gerador = GERADORES.get(processo["id"], documento_outro)
    titulo, corpo = gerador(fake, rng, sinais)
    return titulo, cabecalho_documento(processo["id"], fake, rng, sinais) + corpo


def sortear_sinais(
    processo_id: str, config: dict[str, Any], rng: random.Random
) -> set[str]:
    permitidos = set(
        config.get("sinais_permitidos", {}).get(processo_id, ["nif", "iban"])
    )
    probabilidades = config.get("probabilidades_sinais", {})
    sinais: set[str] = set()

    if processo_id == "saude" and "dados_clinicos" in permitidos:
        sinais.add("dados_clinicos")

    publicavel = processo_id in set(config.get("processos_publicaveis", []))
    if (
        publicavel
        and "publicacao_autorizada" in permitidos
        and rng.random() < probabilidades.get("publicacao_autorizada", 0.0)
    ):
        sinais.add("publicacao_autorizada")

    if "publicacao_autorizada" not in sinais:
        for sinal in ("credenciais", "iban"):
            if sinal in permitidos and rng.random() < probabilidades.get(sinal, 0.0):
                sinais.add(sinal)

    if "nif" in permitidos and rng.random() < probabilidades.get("nif", 0.0):
        sinais.add("nif")

    return sinais


def dimensoes_base(
    processo: dict[str, Any], config: dict[str, Any]
) -> dict[str, str]:
    pre_qualificacao = processo.get("pre_qualificacao_provisoria")
    origem = pre_qualificacao or config["dimensoes_padrao"]
    return {
        dimensao: origem.get(dimensao, "S")
        for dimensao in ("pessoas", "estado", "exposicao")
    }


def aplicar_efeitos_conteudo(
    base: dict[str, str], sinais: set[str], config: dict[str, Any]
) -> dict[str, str]:
    dimensoes = dict(base)
    efeitos = config.get("efeitos_conteudo", {})
    for sinal in sorted(sinais):
        for dimensao, efeito in efeitos.get(sinal, {}).items():
            if isinstance(efeito, str) and efeito.startswith("+"):
                incremento = int(efeito[1:])
                valor = min(2, ESCALA[dimensoes[dimensao]] + incremento)
                dimensoes[dimensao] = ESCALA_INV[valor]
            else:
                dimensoes[dimensao] = ESCALA_INV[
                    max(ESCALA[dimensoes[dimensao]], ESCALA[efeito])
                ]
    return dimensoes


def calcular_classe(
    processo_id: str,
    sinais: set[str],
    config: dict[str, Any],
    empresa: dict[str, Any],
) -> str:
    classe = config.get("classe_base_por_processo", {}).get(
        processo_id, "uso_interno"
    )
    regras = {
        regra["sinal"]: regra
        for regra in empresa.get("regras_preliminares", [])
    }
    impeditivos = sinais & {"iban", "dados_clinicos", "credenciais"}

    for sinal in sorted(sinais):
        regra = regras.get(SINAL_PARA_REGRA.get(sinal))
        if regra is None:
            continue
        efeito = regra.get("efeito")
        if efeito == "classe_minima":
            minima = regra["classe"]
            if ORDEM_CLASSE[minima] > ORDEM_CLASSE[classe]:
                classe = minima
        elif efeito == "permite_publico_se_ausencia_de_sinais_sensiveis":
            if (
                sinal == "publicacao_autorizada"
                and not impeditivos
                and ORDEM_CLASSE[classe] <= ORDEM_CLASSE["uso_interno"]
            ):
                classe = "publico"

    return classe


def justificacao(
    processo_nome: str, sinais: set[str], classe: str
) -> str:
    partes = [
        descricao
        for sinal, descricao in ORDEM_JUSTIFICACAO
        if sinal in sinais
    ]
    if partes:
        inicio = f"Contém {', '.join(partes)}"
    else:
        inicio = "Sem sinais sensíveis detetados"
    return (
        f"{inicio}; processo de {processo_nome}. "
        f"Classe {classe} atribuída pela regra provisória."
    )


def escrever_pdf(caminho: Path, titulo: str, paragrafos: list[str]) -> None:
    documento = pymupdf.open()
    largura, altura = pymupdf.paper_size("a4")
    margem = 56.0
    y = margem

    def nova_pagina():
        nonlocal y
        pagina = documento.new_page(width=largura, height=altura)
        y = margem
        pagina.insert_text(
            (margem, altura - 30),
            "Documento sintético - sem valor legal",
            fontsize=8,
            fontname="helv",
            color=(0.45, 0.45, 0.45),
        )
        return pagina

    pagina = nova_pagina()
    for linha in textwrap.wrap(titulo, width=60) or [titulo]:
        if y > altura - margem:
            pagina = nova_pagina()
        pagina.insert_text((margem, y), linha, fontsize=16, fontname="hebo")
        y += 22

    y += 10
    for paragrafo in paragrafos:
        if not paragrafo.strip():
            y += 8
            continue
        linhas = textwrap.wrap(
            paragrafo,
            width=92,
            break_long_words=False,
            break_on_hyphens=False,
        )
        for linha in linhas or [""]:
            if y > altura - margem:
                pagina = nova_pagina()
            pagina.insert_text((margem, y), linha, fontsize=10.5, fontname="helv")
            y += 14.5
        y += 6

    documento.set_metadata(
        {
            "title": titulo,
            "author": "ContextIQ - corpus sintético",
            "subject": "Documento sintético para classificação",
            "creator": "ContextIQ",
            "producer": "PyMuPDF",
            "creationDate": "D:20260101000000Z",
            "modDate": "D:20260101000000Z",
        }
    )
    documento.save(str(caminho), garbage=4, deflate=True)
    documento.close()


def escrever_docx(caminho: Path, titulo: str, paragrafos: list[str]) -> None:
    documento = Document()
    documento.add_heading(titulo, level=1)
    for paragrafo in paragrafos:
        documento.add_paragraph(paragrafo)

    propriedades = documento.core_properties
    propriedades.author = "ContextIQ - corpus sintético"
    propriedades.title = titulo
    propriedades.subject = "Documento sintético para classificação"

    documento.save(str(caminho))


def hash_sha256(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def atribuir_split(
    registos: list[dict[str, Any]], proporcao: float, seed: int
) -> None:
    rng = random.Random(seed)
    grupos: dict[str, list[str]] = defaultdict(list)
    for registo in registos:
        grupos[registo["processo"]].append(registo["id"])

    atribuicoes: dict[str, str] = {}
    for ids in grupos.values():
        rng.shuffle(ids)
        n_teste = max(1, round(len(ids) * proporcao))
        for indice, doc_id in enumerate(ids):
            atribuicoes[doc_id] = "teste" if indice < n_teste else "treino"

    for registo in registos:
        registo["split"] = atribuicoes[registo["id"]]


def contagens(registos: list[dict[str, Any]], campo: str) -> dict[str, int]:
    resultado: dict[str, int] = {}
    for registo in registos:
        valor = str(registo[campo])
        resultado[valor] = resultado.get(valor, 0) + 1
    return dict(sorted(resultado.items()))


def escrever_etiquetas(caminho: Path, registos: list[dict[str, Any]]) -> None:
    with caminho.open("w", encoding="utf-8", newline="") as ficheiro:
        escritor = csv.DictWriter(ficheiro, fieldnames=CABECALHO_ETIQUETAS)
        escritor.writeheader()
        for registo in sorted(registos, key=lambda item: item["id"]):
            escritor.writerow(
                {campo: registo[campo] for campo in CABECALHO_ETIQUETAS}
            )


def limpar_destino(destino: Path) -> None:
    if not destino.exists():
        return
    proibidos = {RAIZ_PROJETO.resolve(), DIRETORIA_CONFIG.resolve()}
    if destino.resolve() in proibidos:
        raise ValueError(f"Destino recusado para limpeza: {destino}")
    shutil.rmtree(destino)


def gerar_corpus(
    destino: str | Path | None = None,
    por_processo: int | None = None,
    seed: int | None = None,
    limpar: bool = False,
) -> list[dict[str, Any]]:
    config = carregar_config_corpus()
    processos = carregar_processos()
    empresa = carregar_taxonomia_empresa()

    seed = int(config["seed"] if seed is None else seed)
    por_processo = int(
        config["por_processo"] if por_processo is None else por_processo
    )
    if por_processo < 1:
        raise ValueError("por_processo tem de ser pelo menos 1")

    destino = resolver_caminho(destino or config["diretoria_saida"])
    if limpar:
        limpar_destino(destino)

    diretorio_documentos = destino / "documentos"
    if diretorio_documentos.exists() and any(diretorio_documentos.iterdir()):
        raise FileExistsError(
            f"{diretorio_documentos} já contém ficheiros; use limpar=True "
            "ou a opção --limpar para regenerar."
        )
    diretorio_documentos.mkdir(parents=True, exist_ok=True)

    tarefas = [
        processo
        for processo in processos
        for _ in range(por_processo)
    ]
    rng = random.Random(seed)
    rng.shuffle(tarefas)

    total = len(tarefas)
    n_pdf = round(total * float(config.get("proporcao_pdf", 0.5)))
    formatos = ["pdf"] * n_pdf + ["docx"] * (total - n_pdf)
    rng.shuffle(formatos)

    fake = Faker("pt_PT")
    fake.seed_instance(seed)

    registos: list[dict[str, Any]] = []
    for indice, processo in enumerate(tarefas):
        sinais = sortear_sinais(processo["id"], config, rng)
        dimensoes = aplicar_efeitos_conteudo(
            dimensoes_base(processo, config), sinais, config
        )
        classe = calcular_classe(processo["id"], sinais, config, empresa)
        titulo, paragrafos = compor_documento(processo, fake, rng, sinais)

        doc_id = f"doc-{indice + 1:04d}"
        formato = formatos[indice]
        caminho = diretorio_documentos / f"{doc_id}.{formato}"
        if formato == "pdf":
            escrever_pdf(caminho, titulo, paragrafos)
        else:
            escrever_docx(caminho, titulo, paragrafos)

        try:
            ficheiro = caminho.relative_to(RAIZ_PROJETO).as_posix()
        except ValueError:
            ficheiro = caminho.as_posix()

        registos.append(
            {
                "id": doc_id,
                "ficheiro": ficheiro,
                "formato": formato,
                "processo": processo["id"],
                "pessoas": dimensoes["pessoas"],
                "estado": dimensoes["estado"],
                "exposicao": dimensoes["exposicao"],
                "classe": classe,
                "sinais": ";".join(sorted(sinais)),
                "justificacao": justificacao(
                    processo["nome"], sinais, classe
                ),
                "split": "",
                "hash_sha256": hash_sha256(caminho),
            }
        )

    atribuir_split(
        registos, float(config.get("proporcao_teste", 0.2)), seed + 1
    )
    escrever_etiquetas(destino / "etiquetas.csv", registos)

    manifesto = {
        "versao": config.get("versao"),
        "seed": seed,
        "por_processo": por_processo,
        "total": total,
        "formatos": contagens(registos, "formato"),
        "processos": contagens(registos, "processo"),
        "classes": contagens(registos, "classe"),
        "splits": contagens(registos, "split"),
        "dimensoes": {
            "pessoas": contagens(registos, "pessoas"),
            "estado": contagens(registos, "estado"),
            "exposicao": contagens(registos, "exposicao"),
        },
        "aviso": (
            "Corpus sintético gerado para fins académicos. As etiquetas seguem "
            "uma regra provisória e não o referencial oficial do CNCS e da ARTE."
        ),
    }
    with (destino / "manifesto.json").open("w", encoding="utf-8") as ficheiro:
        json.dump(manifesto, ficheiro, ensure_ascii=False, indent=2)

    return registos
