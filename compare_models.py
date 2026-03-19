from __future__ import annotations

import argparse
from textwrap import wrap

from github_models_compare import CompareConfig, DEFAULT_MODELS, compare_models, mock_results, resolve_token


DEFAULT_PROMPT = "Compare as respostas sobre cura energética, separando crença, evidência, limites e riscos."


def parse_models(values: list[str] | None) -> list[tuple[str, str]]:
    if not values:
        return DEFAULT_MODELS
    parsed: list[tuple[str, str]] = []
    for value in values:
        parts = value.split("=", 1)
        if len(parts) != 2:
            raise SystemExit(f"Modelo inválido: {value}. Use LABEL=model_id")
        parsed.append((parts[0].strip(), parts[1].strip()))
    return parsed


def render_side_by_side(results, width: int = 28) -> str:
    wrapped_columns = []
    for result in results:
        body = result.content if result.ok else f"ERRO: {result.error}"
        lines = [result.label, result.model_id, ""] + wrap(body, width=width)[:18]
        wrapped_columns.append(lines)

    max_lines = max(len(lines) for lines in wrapped_columns)
    normalized = [lines + [""] * (max_lines - len(lines)) for lines in wrapped_columns]
    separator = " | "
    header = separator.join(line[0].ljust(width) for line in normalized)
    underline = separator.join("-" * width for _ in normalized)
    rows = [header, underline]
    for row_index in range(1, max_lines):
        rows.append(separator.join(column[row_index].ljust(width) for column in normalized))
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare respostas de vários modelos via GitHub Models.")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--system-prompt", default="Você compara respostas em português do Brasil com foco em clareza.")
    parser.add_argument("--model", action="append", help="Use LABEL=model_id. Pode ser repetido.")
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--token", default="")
    parser.add_argument("--mock", action="store_true", help="Usa respostas simuladas para testar o layout.")
    args = parser.parse_args()

    models = parse_models(args.model)
    if args.mock:
        results = mock_results(args.prompt, models)
    else:
        token = resolve_token(args.token)
        if not token:
            raise SystemExit("Defina GITHUB_TOKEN/GH_TOKEN ou use --token/--mock.")
        config = CompareConfig(
            token=token,
            prompt=args.prompt,
            system_prompt=args.system_prompt,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            timeout_seconds=args.timeout,
        )
        results = compare_models(config, models)

    print(render_side_by_side(results))


if __name__ == "__main__":
    main()
