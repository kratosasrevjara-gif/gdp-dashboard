# 🧠 AI response comparison lab

Este app Streamlit compara respostas de múltiplos modelos em paralelo usando o endpoint do GitHub Models.

## O que ele faz

- Envia o mesmo prompt para GPT, Claude, Gemini e DeepSeek.
- Mostra um resumo tabular com status HTTP, tokens e um preview.
- Exibe as respostas lado a lado para facilitar comparação qualitativa.
- Inclui um prompt de sistema mais cuidadoso para temas sensíveis, como saúde e bem-estar.
- Permite trocar os `model_id`s caso o catálogo do GitHub Models mude.

## Como executar

1. Instale as dependências.

   ```bash
   pip install -r requirements.txt
   ```

2. Defina um token do GitHub com acesso ao GitHub Models.

   ```bash
   export GITHUB_TOKEN=seu_token_aqui
   ```

3. Rode o app.

   ```bash
   streamlit run streamlit_app.py
   ```

## Endpoint usado

O app usa o endpoint REST do GitHub Models:

- `POST https://models.github.ai/inference/chat/completions`

## Observações

- O GitHub Models tem uma camada gratuita com limites de uso.
- A disponibilidade de modelos pode variar ao longo do tempo; se um `model_id` deixar de funcionar, ajuste o campo na interface.
- Para temas de saúde, compare criticamente respostas que façam promessas terapêuticas sem base robusta.
