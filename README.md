# Concílio Sagrado de IAs

Aplicativo Streamlit para comparar respostas de **GPT**, **Claude**, **Gemini**, **DeepSeek** e opcionalmente **Qwen** lado a lado usando **GitHub Models**.

## O que o app oferece

- campo para **GitHub token**;
- campo para **prompt**;
- campo para **system prompt**;
- seleção rápida dos modelos ativos;
- respostas renderizadas lado a lado;
- tabela comparativa com status, tempo e resumo;
- exportação das respostas completas em `.txt`;
- modo simulado para testar a interface sem token.

## Como executar

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py --server.headless true --server.port 8501
```

## Endpoint usado

```text
POST https://models.github.ai/inference/chat/completions
```

## Token

Use um token pessoal do GitHub compatível com GitHub Models. Se o token for fine-grained, garanta acesso de leitura a modelos.

## Observação importante

O app permite comparar respostas para temas espirituais, energéticos e afins, mas as saídas devem ser tratadas como **texto gerado por modelos** — não como validação factual, orientação clínica ou garantia de efeito no mundo real.
