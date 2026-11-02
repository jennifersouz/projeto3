from __future__ import annotations

import argparse
import sys
from pathlib import Path


RAIZ_PROJETO = Path(__file__).resolve().parents[1]
DIRETORIA_SRC = RAIZ_PROJETO / "src"
if str(DIRETORIA_SRC) not in sys.path:
    sys.path.insert(0, str(DIRETORIA_SRC))

from motor.corpus import contagens, gerar_corpus


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Gera o corpus sintético etiquetado do ContextIQ."
    )
    parser.add_argument(
        "--destino",
        type=Path,
        default=None,
        help="Diretório de saída (predefinição: dados/corpus).",
    )
    parser.add_argument(
        "--por-processo",
        type=int,
        default=None,
        help="Número de documentos por processo (predefinição: 50).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Semente para geração reprodutível (predefinição: 4900).",
    )
    parser.add_argument(
        "--limpar",
        action="store_true",
        help="Apaga o destino antes de gerar.",
    )
    args = parser.parse_args(argv)

    try:
        registos = gerar_corpus(
            destino=args.destino,
            por_processo=args.por_processo,
            seed=args.seed,
            limpar=args.limpar,
        )
    except (FileExistsError, ValueError) as erro:
        parser.exit(2, f"Erro: {erro}\n")

    print(f"Corpus gerado: {len(registos)} documentos")
    print(f"Processos: {contagens(registos, 'processo')}")
    print(f"Formatos: {contagens(registos, 'formato')}")
    print(f"Classes: {contagens(registos, 'classe')}")
    print(f"Splits: {contagens(registos, 'split')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
