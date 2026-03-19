---
title: Concilio Sagrado de IAs
emoji: 🔮
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 7860
python_version: 3.10
fullWidth: true
short_description: Compare GPT, Claude, Gemini, DeepSeek e Qwen via GitHub Models.
---

# Concílio Sagrado de IAs

Aplicativo Streamlit para comparar respostas de **GPT**, **Claude**, **Gemini**, **DeepSeek** e opcionalmente **Qwen** lado a lado usando **GitHub Models**.

## Link público e permanente no Hugging Face Spaces

## Para você agora (login `kratos`)

## Se você só tem GitHub, este é o caminho mais fácil

Use **Streamlit Community Cloud**. As docs oficiais do Streamlit dizem que o serviço é grátis, conecta direto ao GitHub e publica apps em subdomínios `streamlit.app`.

Passo mínimo para o seu caso:

1. Abra <https://share.streamlit.io>
2. Clique em **Continue with GitHub**
3. Clique em **Create app**
4. Escolha o repositório `kratosasrevjara-gif/gdp-dashboard`
5. Em **Branch**, escolha `main`
6. Em **Main file path**, use `app.py`
7. Clique em **Deploy**

O link público ficará em um subdomínio `streamlit.app` criado pelo Streamlit, e você pode mudar esse subdomínio depois.

Se você criar o Space com o nome `concilio-sagrado-ias`, os links finais serão:

```text
https://huggingface.co/spaces/kratos/concilio-sagrado-ias
```

```text
https://kratos-concilio-sagrado-ias.hf.space
```

Passo mínimo:

1. Abra <https://huggingface.co/new-space>
2. Em **Owner**, escolha `kratos`
3. Em **Space name**, use `concilio-sagrado-ias`
4. Em **SDK**, escolha **Docker**
5. Faça upload destes arquivos: `streamlit_app.py`, `github_models_compare.py`, `compare_models.py`, `requirements.txt`, `README.md`, `app.py`, `Dockerfile` e a pasta `data/`
6. Espere o build terminar e abra o link

Quando você criar o Space, o link público ficará neste formato:

```text
https://huggingface.co/spaces/SEU_USUARIO/NOME_DO_SPACE
```

E o app rodando também fica acessível no subdomínio `hf.space`:

```text
https://SEU_USUARIO-NOME_DO_SPACE.hf.space
```

## O que você já fez até agora

- Você já criou o código do app Streamlit.
- O app já recebe **token do GitHub**, **prompt** e **system prompt**.
- O app já compara vários modelos lado a lado via **GitHub Models**.
- O app já tem modo simulado, exportação, CLI e testes automatizados.
- O PR já está aberto, então o projeto já está estruturado e pronto para publicação.

Arquivos principais:

- `streamlit_app.py`: interface Streamlit principal.
- `github_models_compare.py`: integração com GitHub Models.
- `compare_models.py`: comparação no terminal.
- `app.py`: entrada simples para deploy no Hugging Face Spaces.
- `Dockerfile`: configuração para publicar no Spaces com Docker.

## Passo a passo mais fácil: subir no Hugging Face Spaces

### 1) Crie sua conta
Acesse: <https://huggingface.co/join>

### 2) Crie um novo Space
Acesse: <https://huggingface.co/new-space>

Preencha assim:
- **Owner**: sua conta
- **Space name**: por exemplo `concilio-sagrado-ias`
- **License**: pode deixar padrão ou escolher a sua
- **Visibility**: `Public`
- **SDK**: **Docker**

> Importante: hoje o próprio Hugging Face documenta que o SDK embutido de Streamlit está **deprecated** e recomenda usar **Docker** para Streamlit.

### 3) Envie os arquivos do projeto
Você tem 2 caminhos simples:

#### Opção A — Upload pelo navegador
Dentro do Space recém-criado:
- clique em **Files**
- clique em **Add file** / **Upload files**
- envie estes arquivos:
  - `streamlit_app.py`
  - `github_models_compare.py`
  - `compare_models.py`
  - `requirements.txt`
  - `README.md`
  - `app.py`
  - `Dockerfile`
  - pasta `data/` se existir no seu repo

#### Opção B — Duplicar/copiar do GitHub
Se o repositório já está no GitHub, você também pode copiar o conteúdo dele para o Space por git. Cada commit novo faz o Space rebuildar automaticamente.

### 4) Espere o build terminar
Depois do upload, o Hugging Face vai fazer o build do Space automaticamente.
Quando ficar pronto, o link público do app estará ativo.

### 5) Abra o link público
Formato esperado:

```text
https://huggingface.co/spaces/SEU_USUARIO/concilio-sagrado-ias
```

ou

```text
https://SEU_USUARIO-concilio-sagrado-ias.hf.space
```

### 6) Use o app
No app publicado:
- cole seu **GitHub token**
- escreva seu **prompt**
- clique para comparar as respostas lado a lado

## Se você quiser fazer uma vez e nunca mais mexer

Eu também deixei um workflow do GitHub Actions pronto em `.github/workflows/sync-to-hf-space.yml`.

Depois que você:
1. criar o Space `kratos/concilio-sagrado-ias` no Hugging Face;
2. criar um token no Hugging Face;
3. salvar esse token no GitHub como secret chamado `HF_TOKEN`;

cada push novo na branch `main` pode atualizar o Space automaticamente.

## Arquivos de deploy já preparados aqui

Este repositório já está preparado para o caminho recomendado no Spaces:

- `README.md` com bloco YAML de configuração do Space
- `Dockerfile` para rodar Streamlit na porta `7860`
- `app.py` como ponto de entrada simples

## Observação importante

O app permite comparar respostas para temas espirituais, energéticos e afins, mas as saídas devem ser tratadas como **texto gerado por modelos** — não como validação factual, orientação clínica ou garantia de efeito no mundo real.
