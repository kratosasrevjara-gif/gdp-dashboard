# GitHub Models comparator + Streamlit

Este projeto entrega um aplicativo Streamlit para comparar respostas de **GPT**, **Claude**, **Gemini** e **DeepSeek** lado a lado usando o gateway do **GitHub Models**.

## O que o app faz

- mostra campos para **Prompt**, **System prompt** e **GitHub token**;
- envia o mesmo prompt para quatro modelos configuráveis;
- exibe um **resumo tabular** e as **quatro respostas lado a lado**;
- suporta um **modo simulado** para testar a interface mesmo sem token;
- mantém o dashboard de PIB original apenas como referência secundária dentro de um expander.

## Como executar

Instale as dependências:

```bash
pip install -r requirements.txt
```

Rode o app:

```bash
streamlit run streamlit_app.py --server.headless true --server.port 8501
```

Depois abra o endereço exibido pelo Streamlit, normalmente `http://localhost:8501`.

## Campos principais da interface

- **Prompt**: a pergunta enviada para todos os modelos.
- **System prompt**: instruções comuns aplicadas antes do prompt do usuário.
- **GitHub token**: token usado no header `Authorization: Bearer ...`.
- **Usar respostas simuladas**: permite validar a experiência sem credenciais.

## Endpoint usado

O app chama:

```text
POST https://models.github.ai/inference/chat/completions
```

A implementação do cliente fica em `github_models_compare.py`.

## Execução via terminal

Também existe um CLI para comparar os mesmos modelos fora da interface:

```bash
python compare_models.py --mock --prompt "Compare respostas sobre cura energética, separando crença, evidência, limites e riscos."
```

Com token real:

```bash
export GITHUB_TOKEN=seu_token_aqui
python compare_models.py --prompt "Compare respostas sobre cura energética, separando crença, evidência, limites e riscos."
```

## Observações importantes

- O acesso real ao GitHub Models depende de um token válido e de disponibilidade/cotas do GitHub.
- Neste ambiente eu consigo deixar o app funcionando e testável; sem um token seu eu não consigo obter respostas reais dos quatro modelos.
- Se você tiver apenas um print de um PR, **não dá para inferir com segurança qual é o repositório GitHub de origem** sem mais metadados visíveis, como URL, nome do autor ou nome do repo.
