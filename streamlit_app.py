from __future__ import annotations

import time

import pandas as pd
import streamlit as st

from github_models_compare import (
    CompareConfig,
    DEFAULT_SYSTEM_PROMPT,
    ModelResult,
    compare_models,
    mock_results,
    resolve_token,
)

st.set_page_config(page_title="Concílio Sagrado de IAs", page_icon="🔮", layout="wide")

DEFAULT_MODEL_SLOTS: list[dict[str, str | bool]] = [
    {"label": "GPT", "model_id": "openai/gpt-4.1", "enabled": True},
    {"label": "Claude", "model_id": "anthropic/claude-sonnet-4.5", "enabled": True},
    {"label": "Gemini", "model_id": "google/gemini-2.5-flash", "enabled": True},
    {"label": "DeepSeek", "model_id": "deepseek/deepseek-v3", "enabled": True},
]
QWEN_OPTION = {"label": "Qwen", "model_id": "qwen/qwen3-32b", "enabled": False}
DEFAULT_PROMPT = (
    "Compare respostas sobre cura energética, separando crença, evidência, limitações, "
    "riscos e próximos passos responsáveis."
)
DEFAULT_SYSTEM = (
    "Você está participando de uma comparação lado a lado entre modelos. Responda em português do Brasil, "
    "com tom respeitoso, clareza e precisão. Em temas espirituais, energéticos ou de saúde, diferencie "
    "interpretações pessoais, crenças, riscos e fatos verificáveis."
)


def build_results_table(results: list[ModelResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        rows.append(
            {
                "Modelo": result.label,
                "Model ID": result.model_id,
                "Status": "ok" if result.ok else "erro",
                "HTTP": result.status_code,
                "Tempo (s)": f"{(result.elapsed_seconds or 0):.2f}",
                "Tokens": (result.usage or {}).get("total_tokens"),
                "Resumo": (result.content or result.error or "")[:180],
            }
        )
    return pd.DataFrame(rows)


def build_export_text(results: list[ModelResult]) -> str:
    blocks = []
    for result in results:
        header = f"=== {result.label} | {result.model_id} ==="
        body = result.content if result.ok else f"ERRO: {result.error}"
        blocks.append(f"{header}\nTempo: {(result.elapsed_seconds or 0):.2f}s\n\n{body}")
    return "\n\n---\n\n".join(blocks)


def render_header() -> None:
    st.title("🔮 Concílio Sagrado de IAs")
    st.markdown(
        """
        <div style='text-align: center'>
            <h3>Compare GPT, Claude, Gemini, DeepSeek e Qwen lado a lado via GitHub Models.</h3>
            <p>Cole seu token, escreva o prompt e veja as respostas em paralelo.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Uso temático/ritual opcional. Para temas espirituais, energéticos ou de saúde, trate as respostas "
        "como comparação de linguagem dos modelos, não como validação factual ou orientação clínica."
    )


def render_sidebar() -> tuple[str, float, str, bool, int, int]:
    with st.sidebar:
        st.header("⚙️ Portal de Configuração")
        github_token = st.text_input(
            "🔑 Token do GitHub Models",
            type="password",
            value=resolve_token(),
            help="Use um PAT do GitHub com acesso a models.",
        )
        temperature = st.slider(
            "🌡️ Temperatura (criatividade)",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
        )
        system_prompt = st.text_area(
            "📜 System Prompt",
            value=DEFAULT_SYSTEM_PROMPT if DEFAULT_SYSTEM_PROMPT else DEFAULT_SYSTEM,
            height=160,
        )
        max_tokens = st.slider("🧾 Max tokens", min_value=128, max_value=4096, value=1200, step=64)
        timeout_seconds = st.slider("⏱️ Timeout (s)", min_value=10, max_value=120, value=60, step=5)
        use_mock = st.checkbox("🧪 Usar respostas simuladas", value=not bool(github_token))

        st.markdown("---")
        st.markdown("### 🤖 Modelos sugeridos")
        st.markdown(
            "- `openai/gpt-4.1`\n"
            "- `anthropic/claude-sonnet-4.5`\n"
            "- `google/gemini-2.5-flash`\n"
            "- `deepseek/deepseek-v3`\n"
            "- `qwen/qwen3-32b`"
        )

    return github_token, temperature, system_prompt, use_mock, max_tokens, timeout_seconds


def render_model_selector() -> list[tuple[str, str]]:
    st.header("🤖 Seleção do Concílio")
    active_models: list[tuple[str, str]] = []
    columns = st.columns(len(DEFAULT_MODEL_SLOTS))
    for index, (column, model) in enumerate(zip(columns, DEFAULT_MODEL_SLOTS), start=1):
        with column:
            label = st.text_input(f"Rótulo {index}", value=str(model["label"]), key=f"label_{index}")
            model_id = st.text_input(f"Modelo {index}", value=str(model["model_id"]), key=f"model_{index}")
            enabled = st.checkbox("Ativar", value=bool(model["enabled"]), key=f"enabled_{index}")
            if enabled and model_id.strip():
                active_models.append((label.strip() or f"Modelo {index}", model_id.strip()))

    use_qwen = st.checkbox("🔮 Ativar também Qwen", value=bool(QWEN_OPTION["enabled"]))
    if use_qwen:
        active_models.append((str(QWEN_OPTION["label"]), str(QWEN_OPTION["model_id"])))

    return active_models


def render_result_cards(results: list[ModelResult]) -> None:
    st.header("📜 Respostas do Concílio")
    columns = st.columns(len(results))
    for column, result in zip(columns, results):
        with column:
            st.subheader(f"🤖 {result.label}")
            st.caption(f"{result.model_id} · Tempo: {(result.elapsed_seconds or 0):.2f}s")
            if result.ok:
                st.markdown(result.content or "(sem conteúdo retornado)")
            else:
                status = f"HTTP {result.status_code}" if result.status_code else "Erro de conexão"
                st.error(f"{status}: {result.error}")


def render_footer() -> None:
    with st.expander("ℹ️ Como obter seu token do GitHub Models"):
        st.markdown(
            """
            1. Acesse `github.com/settings/tokens`.
            2. Gere um token pessoal compatível com GitHub Models.
            3. Se o token for fine-grained, garanta a permissão **models: read**.
            4. Cole o token no campo lateral e execute a comparação.
            """
        )
    st.markdown("---")
    st.caption("🔮 Portal do Concílio Sagrado · comparação lado a lado via GitHub Models")


def main() -> None:
    render_header()
    github_token, temperature, system_prompt, use_mock, max_tokens, timeout_seconds = render_sidebar()
    active_models = render_model_selector()

    st.header("📝 Invocação")
    prompt = st.text_area(
        "Digite seu prompt para o concílio:",
        value=DEFAULT_PROMPT,
        height=180,
    )

    st.info(
        "Endpoint usado: POST https://models.github.ai/inference/chat/completions. "
        "Sem token, ative o modo simulado para testar a interface."
    )

    if st.button("🔮 INVOCAR CONCÍLIO", type="primary", use_container_width=True):
        if not active_models:
            st.warning("Selecione pelo menos um modelo para comparar.")
            render_footer()
            return

        if not github_token and not use_mock:
            st.error("Token do GitHub é obrigatório quando o modo simulado está desativado.")
            render_footer()
            return

        progress_bar = st.progress(0.0, text="Preparando o concílio...")
        start_time = time.perf_counter()

        if use_mock:
            progress_bar.progress(0.35, text="Gerando respostas simuladas...")
            results = mock_results(prompt, active_models)
        else:
            progress_bar.progress(0.35, text="Consultando GitHub Models...")
            config = CompareConfig(
                token=github_token,
                prompt=prompt,
                system_prompt=system_prompt or DEFAULT_SYSTEM,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout_seconds=timeout_seconds,
                max_workers=len(active_models),
            )
            results = compare_models(config, active_models)

        progress_bar.progress(1.0, text="Comparação concluída.")
        time.sleep(0.2)
        progress_bar.empty()

        elapsed = time.perf_counter() - start_time
        st.success(f"Comparação finalizada em {elapsed:.2f}s.")
        render_result_cards(results)

        st.header("📊 Análise Comparativa")
        summary_df = build_results_table(results)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.download_button(
            label="📥 Exportar respostas completas",
            data=build_export_text(results),
            file_name=f"concilio_sagrado_{int(time.time())}.txt",
            mime="text/plain",
        )

    render_footer()


if __name__ == "__main__":
    main()
