from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Iterable

import requests

DEFAULT_API_VERSION = "2026-03-10"
DEFAULT_ENDPOINT = "https://models.github.ai/inference/chat/completions"
DEFAULT_MODELS: list[tuple[str, str]] = [
    ("GPT", "openai/gpt-4.1"),
    ("Claude", "anthropic/claude-sonnet-4.5"),
    ("Gemini", "google/gemini-2.5-flash"),
    ("DeepSeek", "deepseek/deepseek-v3"),
]
DEFAULT_SYSTEM_PROMPT = (
    "Você está ajudando a comparar respostas de modelos. Responda em português do Brasil, "
    "com clareza, e diferencie fatos, crenças e incertezas, especialmente em temas de saúde."
)


@dataclass
class ModelResult:
    label: str
    model_id: str
    ok: bool
    content: str
    status_code: int | None = None
    error: str | None = None
    usage: dict[str, Any] | None = None
    elapsed_seconds: float | None = None


@dataclass
class CompareConfig:
    token: str
    prompt: str
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    temperature: float = 0.3
    max_tokens: int = 700
    timeout_seconds: int = 45
    api_version: str = DEFAULT_API_VERSION
    endpoint: str = DEFAULT_ENDPOINT
    max_workers: int = 4


def resolve_token(explicit_token: str | None = None) -> str:
    return (explicit_token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or "").strip()


def infer_via_github_models(config: CompareConfig, model_id: str, label: str) -> ModelResult:
    headers = {
        "Authorization": f"Bearer {config.token}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": config.api_version,
    }
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": config.system_prompt},
            {"role": "user", "content": config.prompt},
        ],
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "stream": False,
    }

    started_at = time.perf_counter()

    try:
        response = requests.post(
            config.endpoint,
            headers=headers,
            json=payload,
            timeout=config.timeout_seconds,
        )
    except requests.RequestException as exc:
        return ModelResult(
            label=label,
            model_id=model_id,
            ok=False,
            content="",
            error=str(exc),
            elapsed_seconds=time.perf_counter() - started_at,
        )

    if not response.ok:
        return ModelResult(
            label=label,
            model_id=model_id,
            ok=False,
            content="",
            status_code=response.status_code,
            error=(response.text or "Erro sem corpo retornado pelo gateway.")[:800],
            elapsed_seconds=time.perf_counter() - started_at,
        )

    data = response.json()
    message = ((data.get("choices") or [{}])[0]).get("message", {})
    content = message.get("content", "")
    if isinstance(content, list):
        content = "\n".join(part.get("text", "") for part in content if isinstance(part, dict))

    return ModelResult(
        label=label,
        model_id=model_id,
        ok=True,
        content=(content or "").strip(),
        status_code=response.status_code,
        usage=data.get("usage"),
        elapsed_seconds=time.perf_counter() - started_at,
    )


def compare_models(config: CompareConfig, models: Iterable[tuple[str, str]]) -> list[ModelResult]:
    ordered_models = list(models)
    if not ordered_models:
        return []

    max_workers = min(max(config.max_workers, 1), len(ordered_models))
    results_by_index: dict[int, ModelResult] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(infer_via_github_models, config, model_id, label): index
            for index, (label, model_id) in enumerate(ordered_models)
        }
        for future in as_completed(future_map):
            index = future_map[future]
            try:
                results_by_index[index] = future.result()
            except Exception as exc:  # defensive fallback for unexpected failures
                label, model_id = ordered_models[index]
                results_by_index[index] = ModelResult(
                    label=label,
                    model_id=model_id,
                    ok=False,
                    content="",
                    error=f"Falha inesperada: {exc}",
                )
    return [results_by_index[index] for index in range(len(ordered_models))]


def mock_results(prompt: str, models: Iterable[tuple[str, str]]) -> list[ModelResult]:
    prompt_preview = " ".join(prompt.split())[:120]
    templates = {
        "GPT": "Enfatiza estrutura e separa hipótese, simbolismo e pedido operacional.",
        "Claude": "Tende a responder com cautela, contextualizando linguagem espiritual como expressão pessoal.",
        "Gemini": "Resume o pedido em blocos e destaca próximos passos práticos antes de interpretações amplas.",
        "DeepSeek": "Costuma ser direto e comparativo, focando nos elementos repetidos do texto enviado.",
    }
    results: list[ModelResult] = []
    for index, (label, model_id) in enumerate(models, start=1):
        summary = templates.get(label, "Resposta simulada para comparação de layout.")
        results.append(
            ModelResult(
                label=label,
                model_id=model_id,
                ok=True,
                content=(
                    f"[simulado] Modelo {label} recebeu o prompt: {prompt_preview}\n\n"
                    f"Leitura resumida {index}: {summary}"
                ),
                status_code=200,
                usage={"total_tokens": 100 + index * 7},
            )
        )
    return results
