from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


RAIZ_PROJETO = Path(__file__).resolve().parents[1]
DIRETORIA_SRC = RAIZ_PROJETO / "src"
if str(DIRETORIA_SRC) not in sys.path:
    sys.path.insert(0, str(DIRETORIA_SRC))

from motor.kappa import (
    CAMPOS_ANOTACAO,
    comparar_anotadores,
    ler_anotacoes,
    validar_anotacoes,
)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description=(
            "Calcula o kappa de Cohen entre duas folhas de anotação "
            "independentes."
        )
    )
    parser.add_argument(
        "--a",
        type=Path,
        default=Path("dados/anotacao/anotador_a.csv"),
        help="Folha do anotador A.",
    )
    parser.add_argument(
        "--b",
        type=Path,
        default=Path("dados/anotacao/anotador_b.csv"),
        help="Folha do anotador B.",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=Path("dados/anotacao/kappa.json"),
        help="Ficheiro JSON com o resultado.",
    )
    parser.add_argument(
        "--minimo",
        type=float,
        default=0.61,
        help="Kappa macro mínimo para considerar a amostra aceitável.",
    )
    args = parser.parse_args(argv)

    try:
        anotador_a = ler_anotacoes(args.a)
        anotador_b = ler_anotacoes(args.b)
        validar_anotacoes(anotador_a, "anotador_a")
        validar_anotacoes(anotador_b, "anotador_b")
        resultado = comparar_anotadores(anotador_a, anotador_b)
    except (FileNotFoundError, ValueError) as erro:
        parser.exit(2, f"Erro: {erro}\n")

    resultado["minimo"] = args.minimo
    resultado["aprovado"] = resultado["kappa_macro"] >= args.minimo
    resultado["gerado_em"] = datetime.now(timezone.utc).isoformat()

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with args.saida.open("w", encoding="utf-8") as ficheiro:
        json.dump(resultado, ficheiro, ensure_ascii=False, indent=2)

    print(f"{'Campo':<12} {'n':>4} {'Acordo':>8} {'Kappa':>8}  Força")
    for campo in CAMPOS_ANOTACAO:
        dados = resultado["campos"][campo]
        print(
            f"{campo:<12} {dados['n']:>4} "
            f"{dados['acordo_observado']:>8.3f} "
            f"{dados['kappa']:>8.3f}  {dados['forca']}"
        )
    print(
        f"{'Conjunto':<12} {resultado['n']:>4} "
        f"{'':>8} {resultado['kappa_conjunto']:>8.3f}  "
        f"{resultado['forca_conjunto']}"
    )
    print(
        f"Kappa macro: {resultado['kappa_macro']:.3f} "
        f"({resultado['forca_macro']}); "
        f"mínimo exigido: {args.minimo:.2f}."
    )
    print(f"Resultado guardado em {args.saida}")

    return 0 if resultado["aprovado"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
