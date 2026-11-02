from __future__ import annotations

import argparse
import sys
from pathlib import Path


RAIZ_PROJETO = Path(__file__).resolve().parents[1]
DIRETORIA_SRC = RAIZ_PROJETO / "src"
if str(DIRETORIA_SRC) not in sys.path:
    sys.path.insert(0, str(DIRETORIA_SRC))

from motor.extracao import extrair_texto


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Extrai o texto de um ficheiro PDF ou DOCX."
    )
    parser.add_argument(
        "caminho",
        nargs="?",
        default="examples/0001100011.pdf",
        help="Ficheiro a extrair (predefinição: examples/0001100011.pdf).",
    )
    args = parser.parse_args(argv)

    try:
        texto = extrair_texto(args.caminho)
    except (FileNotFoundError, ValueError) as erro:
        parser.exit(2, f"Erro: {erro}\n")

    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
