"""CLI de classificação.

Uso:

    uv run python scripts/classificar.py dados/corpus/documentos --taxonomy empresa
    uv run python scripts/classificar.py dados/corpus/documentos --taxonomy pncs

O mesmo lote é analisado uma vez (camada 1, regras); a taxonomia
escolhida só traduz os sinais numa classe. Saída: inventário JSON em
dados/classificacao/ e resumo no ecrã.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import typer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from motor.classificacao import classificar_texto
from motor.config import resolver_caminho
from motor.extracao import extrair_texto

app = typer.Typer(help="Classificador de documentos (camada 1: regras).")

FORMATOS = {".pdf", ".docx"}


def _listar_documentos(caminho: Path) -> list[Path]:
    if caminho.is_file():
        return [caminho]
    return sorted(
        p for p in caminho.rglob("*") if p.suffix.lower() in FORMATOS and p.is_file()
    )


@app.command()
def main(
    alvo: str = typer.Argument(
        ..., help="Ficheiro ou diretoria de documentos (PDF/DOCX)."
    ),
    taxonomy: str = typer.Option(
        "empresa",
        "--taxonomy",
        "-t",
        help="Taxonomia a aplicar: empresa ou pncs.",
    ),
    saida: str | None = typer.Option(
        None,
        "--saida",
        "-o",
        help="Caminho do JSON de saída. Por omissão: dados/classificacao/<taxonomy>.json",
    ),
) -> None:
    classificar(alvo, taxonomy, saida)


def classificar(alvo: str, taxonomy: str, saida: str | None) -> None:
    if taxonomy not in {"empresa", "pncs"}:
        raise typer.BadParameter(f"Taxonomia desconhecida: {taxonomy}")

    raiz = resolver_caminho(alvo)
    documentos = _listar_documentos(raiz)
    if not documentos:
        raise typer.BadParameter(f"Nenhum PDF/DOCX encontrado em: {raiz}")

    linhas: list[dict] = []
    for documento in documentos:
        texto = extrair_texto(documento)
        resultado = classificar_texto(texto, taxonomia=taxonomy)
        resultado["ficheiro"] = documento.name
        linhas.append(resultado)
        typer.echo(
            f"{documento.name:28s} {resultado['processo']:26s} "
            f"{resultado['classe']:12s} {resultado['justificacao']}"
        )

    totais_classe = Counter(linha["classe"] for linha in linhas)
    totais_processo = Counter(linha["processo"] for linha in linhas)
    inventario = {
        "taxonomia": taxonomy,
        "total": len(linhas),
        "totais_classe": dict(sorted(totais_classe.items())),
        "totais_processo": dict(sorted(totais_processo.items())),
        "documentos": linhas,
        "aviso": (
            "Regra provisória; não é o referencial oficial do CNCS e da ARTE."
        ),
    }

    destino = resolver_caminho(
        saida or f"dados/classificacao/{taxonomy}.json"
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8") as ficheiro:
        json.dump(inventario, ficheiro, ensure_ascii=False, indent=2)

    typer.echo(f"\nInventário: {destino}")
    typer.echo(f"Totais por classe: {inventario['totais_classe']}")


if __name__ == "__main__":
    app()
