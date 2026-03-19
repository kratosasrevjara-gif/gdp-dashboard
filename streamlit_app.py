from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import streamlit as st

from github_models_compare import (
    CompareConfig,
    DEFAULT_MODELS,
    DEFAULT_SYSTEM_PROMPT,
    ModelResult,
    compare_models,
    mock_results,
    resolve_token,
)

st.set_page_config(page_title="GitHub Models comparator", page_icon=":robot_face:", layout="wide")


@st.cache_data
def get_gdp_data() -> pd.DataFrame:
    data_filename = Path(__file__).parent / "data/gdp_data.csv"
    raw_gdp_df = pd.read_csv(data_filename)
    gdp_df = raw_gdp_df.melt(
        ["Country Code"],
        [str(x) for x in range(1960, 2023)],
        "Year",
        "GDP",
    )
    gdp_df["Year"] = pd.to_numeric(gdp_df["Year"])
    return gdp_df


def build_results_table(results: list[ModelResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        rows.append(
            {
                "Model": result.label,
                "Model ID": result.model_id,
                "Status": "ok" if result.ok else "error",
                "HTTP": result.status_code,
                "Total tokens": (result.usage or {}).get("total_tokens"),
                "Preview": (result.content or result.error or "")[:140],
            }
        )
    return pd.DataFrame(rows)


def render_gdp_reference() -> None:
    gdp_df = get_gdp_data()
    with st.expander("Ver dashboard de PIB de referência", expanded=False):
        st.caption("Mantido no projeto como exemplo Streamlit original.")
        min_value = int(gdp_df["Year"].min())
        max_value = int(gdp_df["Year"].max())
        from_year, to_year = st.slider(
            "Período do PIB",
            min_value=min_value,
            max_value=max_value,
            value=[min_value, max_value],
        )
        countries = gdp_df["Country Code"].unique()
        selected_countries = st.multiselect(
            "Países",
            countries,
            ["DEU", "FRA", "GBR", "BRA", "MEX", "JPN"],
        )
        filtered_gdp_df = gdp_df[
            (gdp_df["Country Code"].isin(selected_countries))
            & (gdp_df["Year"] <= to_year)
            & (from_year <= gdp_df["Year"])
        ]
        st.line_chart(filtered_gdp_df, x="Year", y="GDP", color="Country Code")
        first_year = gdp_df[gdp_df["Year"] == from_year]
        last_year = gdp_df[gdp_df["Year"] == to_year]
        cols = st.columns(4)
        for index, country in enumerate(selected_countries):
            with cols[index % len(cols)]:
                first_gdp = first_year[first_year["Country Code"] == country]["GDP"].iat[0] / 1_000_000_000
                last_gdp = last_year[last_year["Country Code"] == country]["GDP"].iat[0] / 1_000_000_000
                if math.isnan(first_gdp):
                    growth = "n/a"
                    delta_color = "off"
                else:
                    growth = f"{last_gdp / first_gdp:,.2f}x"
                    delta_color = "normal"
                st.metric(
                    label=f"{country} GDP",
                    value=f"{last_gdp:,.0f}B",
                    delta=growth,
                    delta_color=delta_color,
                )


def render_model_inputs() -> list[tuple[str, str]]:
    configured_models: list[tuple[str, str]] = []
    columns = st.columns(len(DEFAULT_MODELS))
    for index, ((default_label, default_model_id), column) in enumerate(zip(DEFAULT_MODELS, columns), start=1):
        with column:
            label = st.text_input(f"Rótulo {index}", value=default_label, key=f"label_{index}")
            model_id = st.text_input(f"Model ID {index}", value=default_model_id, key=f"model_{index}")
            configured_models.append((label.strip() or f"Modelo {index}", model_id.strip()))
    return configured_models


def render_result_cards(results: list[ModelResult]) -> None:
    response_columns = st.columns(len(results))
    for column, result in zip(response_columns, results):
        with column:
            st.markdown(f"### {result.label}")
            st.caption(result.model_id)
            if result.ok:
                st.write(result.content or "(sem conteúdo retornado)")
            else:
                status = f"HTTP {result.status_code}" if result.status_code else "Erro de conexão"
                st.error(f"{status}: {result.error}")


def main() -> None:
    st.title("🧠 Comparador de GPT, Claude, Gemini e DeepSeek")
    st.write(
        "Envie o mesmo prompt para quatro modelos via GitHub Models e veja as respostas lado a lado. "
        "Se você ainda não tiver token, ative o modo simulado para testar a interface grátis aqui mesmo."
    )

    with st.form("compare-form"):
        prompt = st.text_area(
            "Prompt",
            value=(
                "Compare respostas sobre cura energética, separando crença, evidência, limitações, "
                "riscos e próximos passos responsáveis."
            ),
            height=180,
        )
        system_prompt = st.text_area("System prompt", value=DEFAULT_SYSTEM_PROMPT, height=120)

        config_col, options_col = st.columns([1.2, 1])
        with config_col:
            token = st.text_input(
                "GitHub token",
                type="password",
                value=resolve_token(),
                help="Use um token com acesso ao GitHub Models. Ele fica somente nesta sessão do app.",
            )
            use_mock = st.checkbox("Usar respostas simuladas", value=not bool(token))
        with options_col:
            temperature = st.slider("Temperature", min_value=0.0, max_value=1.5, value=0.3, step=0.1)
            max_tokens = st.slider("Max tokens", min_value=128, max_value=2048, value=700, step=64)
            timeout_seconds = st.slider("Timeout (s)", min_value=10, max_value=120, value=45, step=5)

        st.markdown("#### Modelos comparados")
        configured_models = render_model_inputs()
        submitted = st.form_submit_button("Executar comparação", type="primary")

    st.info(
        "Endpoint usado: POST https://models.github.ai/inference/chat/completions. "
        "Sem token válido, o app pode rodar em modo simulado para você validar layout e fluxo."
    )

    if submitted:
        if use_mock:
            results = mock_results(prompt, configured_models)
        else:
            if not token:
                st.error("Preencha o GitHub token ou marque 'Usar respostas simuladas'.")
                return
            config = CompareConfig(
                token=token,
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout_seconds=timeout_seconds,
            )
            with st.spinner("Consultando GitHub Models em paralelo..."):
                results = compare_models(config, configured_models)

        st.subheader("Resumo")
        st.dataframe(build_results_table(results), use_container_width=True, hide_index=True)
        st.subheader("Respostas lado a lado")
        render_result_cards(results)

    render_gdp_reference()


if __name__ == "__main__":
    main()
