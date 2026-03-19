from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="AI response comparison lab", page_icon="🧠", layout="wide")

DEFAULT_PROMPT = (
    "Compare how different AI models respond to this request: 'What is energy healing, "
    "which benefits are supported by evidence, and what should someone know about its "
    "limits and risks?' Answer in Brazilian Portuguese."
)

DEFAULT_MODELS = [
    ("GPT", "openai/gpt-4.1"),
    ("Claude", "anthropic/claude-sonnet-4.5"),
    ("Gemini", "google/gemini-2.5-flash"),
    ("DeepSeek", "deepseek/deepseek-v3"),
]

SYSTEM_PROMPT = (
    "You are an assistant helping a user compare model outputs. Answer clearly in Brazilian "
    "Portuguese. If the topic involves health claims, distinguish established evidence from "
    "beliefs or anecdotal reports, avoid presenting unverified claims as facts, and recommend "
    "professional care for diagnosis or treatment decisions."
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


def infer_via_github_models(
    *,
    token: str,
    model_id: str,
    prompt: str,
    system_prompt: str,
    temperature: float,
    max_tokens: int,
    timeout_seconds: int,
    api_version: str,
) -> ModelResult:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": api_version,
    }
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    try:
        response = requests.post(
            "https://models.github.ai/inference/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout_seconds,
        )
    except requests.RequestException as exc:
        return ModelResult(
            label=model_id.split("/", 1)[0].title(),
            model_id=model_id,
            ok=False,
            content="",
            error=str(exc),
        )

    if not response.ok:
        error_text = response.text.strip()[:600]
        return ModelResult(
            label=model_id.split("/", 1)[0].title(),
            model_id=model_id,
            ok=False,
            content="",
            status_code=response.status_code,
            error=error_text or "GitHub Models returned an empty error response.",
        )

    data = response.json()
    choices = data.get("choices", [])
    message = choices[0].get("message", {}) if choices else {}
    content = message.get("content", "")
    if isinstance(content, list):
        content = "\n".join(part.get("text", "") for part in content if isinstance(part, dict))

    return ModelResult(
        label=model_id.split("/", 1)[0].title(),
        model_id=model_id,
        ok=True,
        content=content.strip(),
        status_code=response.status_code,
        usage=data.get("usage"),
    )


def build_results_table(results: list[ModelResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        total_tokens = None
        if result.usage:
            total_tokens = result.usage.get("total_tokens")
        rows.append(
            {
                "Model": result.label,
                "Model ID": result.model_id,
                "Status": "ok" if result.ok else "error",
                "HTTP": result.status_code,
                "Total tokens": total_tokens,
                "Preview": (result.content or result.error or "")[:140],
            }
        )
    return pd.DataFrame(rows)


st.title("🧠 Painel para comparar GPT, Claude, Gemini e DeepSeek")
st.write(
    "Use um único prompt e veja as respostas lado a lado via GitHub Models. "
    "A interface foi montada para comparar modelos sobre temas sensíveis, incluindo saúde, "
    "sem transformar alegações não verificadas em fatos."
)

with st.sidebar:
    st.header("Configuração")
    token = st.text_input(
        "GitHub token",
        type="password",
        value=os.getenv("GITHUB_TOKEN", "") or os.getenv("GH_TOKEN", ""),
        help="Use um token com acesso ao GitHub Models. Tokens fine-grained precisam de models:read.",
    )
    api_version = st.text_input("API version", value="2026-03-10")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.5, value=0.3, step=0.1)
    max_tokens = st.slider("Max tokens", min_value=128, max_value=2048, value=700, step=64)
    timeout_seconds = st.slider("Timeout (s)", min_value=10, max_value=120, value=45, step=5)
    st.caption(
        "GitHub Models oferece uma faixa gratuita com limites de uso; a disponibilidade e os "
        "modelos exatos podem variar por conta e por data."
    )

st.subheader("Prompt")
prompt = st.text_area("Prompt único para todos os modelos", value=DEFAULT_PROMPT, height=140)
system_prompt = st.text_area("Prompt de sistema", value=SYSTEM_PROMPT, height=120)

st.subheader("Modelos")
model_columns = st.columns(4)
configured_models: list[tuple[str, str]] = []
for index, ((default_label, default_model_id), column) in enumerate(zip(DEFAULT_MODELS, model_columns), start=1):
    with column:
        label = st.text_input(f"Rótulo {index}", value=default_label)
        model_id = st.text_input(f"Model ID {index}", value=default_model_id)
        configured_models.append((label.strip() or f"Modelo {index}", model_id.strip()))

run_clicked = st.button("Executar comparação", type="primary")

if run_clicked:
    missing_model_ids = [label for label, model_id in configured_models if not model_id]
    if missing_model_ids:
        st.error(f"Preencha o model ID de: {', '.join(missing_model_ids)}.")
    elif not token:
        st.warning(
            "Não encontrei um token GitHub no ambiente nem no formulário. "
            "Adicione `GITHUB_TOKEN` ou cole um token acima para buscar respostas reais."
        )
    else:
        results: list[ModelResult] = []
        progress = st.progress(0.0, text="Consultando modelos...")
        for index, (label, model_id) in enumerate(configured_models, start=1):
            result = infer_via_github_models(
                token=token,
                model_id=model_id,
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout_seconds=timeout_seconds,
                api_version=api_version,
            )
            result.label = label
            results.append(result)
            progress.progress(index / len(configured_models), text=f"Consultado: {label}")
        progress.empty()

        st.subheader("Resumo")
        st.dataframe(build_results_table(results), use_container_width=True, hide_index=True)

        st.subheader("Respostas lado a lado")
        response_columns = st.columns(len(results))
        for column, result in zip(response_columns, results):
            with column:
                st.markdown(f"### {result.label}")
                st.caption(result.model_id)
                if result.ok:
                    st.write(result.content or "(sem conteúdo retornado)")
                    if result.usage:
                        st.caption(f"Uso: {result.usage}")
                else:
                    status_label = f"HTTP {result.status_code}" if result.status_code else "Erro de conexão"
                    st.error(f"{status_label}: {result.error}")

        ok_results = [result for result in results if result.ok and result.content]
        if ok_results:
            st.subheader("Comparação rápida")
            st.write(
                "Observe se algum modelo apresenta alegações terapêuticas fortes sem citar limites, "
                "separa evidência de opinião e menciona riscos de adiar cuidados médicos."
            )

with st.expander("Exemplo de script Python equivalente"):
    st.code(
        '''import os
import requests

TOKEN = os.environ["GITHUB_TOKEN"]
MODELS = {
    "GPT": "openai/gpt-4.1",
    "Claude": "anthropic/claude-sonnet-4.5",
    "Gemini": "google/gemini-2.5-flash",
    "DeepSeek": "deepseek/deepseek-v3",
}
PROMPT = "Explique cura energética com foco em evidências, limites e riscos."

for label, model in MODELS.items():
    response = requests.post(
        "https://models.github.ai/inference/chat/completions",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": PROMPT}],
            "temperature": 0.3,
            "max_tokens": 500,
        },
        timeout=45,
    )
    print("\n" + "=" * 80)
    print(label, model)
    print(response.json()["choices"][0]["message"]["content"])
''',
        language="python",
    )
