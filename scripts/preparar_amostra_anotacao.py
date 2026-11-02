from __future__ import annotations

import argparse
import sys
from pathlib import Path


RAIZ_PROJETO = Path(__file__).resolve().parents[1]
DIRETORIA_SRC = RAIZ_PROJETO / "src"
if str(DIRETORIA_SRC) not in sys.path:
    sys.path.insert(0, str(DIRETORIA_SRC))

from motor.anotacao import preparar_amostra_anotacao


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description=(
            "Prepara a amostra de dupla anotação (50 documentos por "
            "predefinição) para calcular o kappa de Cohen."
        )
    )
    parser.add_argument(
        "--etiquetas",
        type=Path,
        default=None,
        help="CSV de etiquetas do corpus (predefinição: dados/corpus/etiquetas.csv).",
    )
    parser.add_argument(
        "--destino",
        type=Path,
        default=None,
        help="Diretório de saída (predefinição: dados/anotacao).",
    )
    parser.add_argument(
        "--tamanho",
        type=int,
        default=None,
        help="Número de documentos da amostra (predefinição: 50).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Semente da seleção (predefinição: 4901).",
    )
    parser.add_argument(
        "--limpar",
        action="store_true",
        help="Substitui folhas de anotação existentes.",
    )
    args = parser.parse_args(argv)

    try:
        manifesto = preparar_amostra_anotacao(
            etiquetas=args.etiquetas,
            destino=args.destino,
            tamanho=args.tamanho,
            seed=args.seed,
            limpar=args.limpar,
        )
    except (FileExistsError, ValueError) as erro:
        parser.exit(2, f"Erro: {erro}\n")

    print(f"Amostra preparada: {manifesto['tamanho']} documentos")
    print(f"Processos: {manifesto['processos']}")
    print("Folhas: anotador_a.csv e anotador_b.csv")
    print("Cada anotador preenche a sua folha de forma independente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
