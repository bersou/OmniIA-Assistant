# 🚀 OmniIA: Seu Assistente de IA Completo!

**OmniIA** é um **assistente inteligente e interativo** construído com **Streamlit**, projetado para turbinar sua produtividade diária. Ele integra um modelo de linguagem avançado com ferramentas modernas de IA — e tudo isso em uma interface simples, direta e eficiente no seu dia a dia.

---

## ✨ Funcionalidades Incríveis

Veja o que o OmniIA pode fazer por você:

- 🤖 **Perguntar ao Assistente IA:**  
  Obtenha respostas fiáveis e precisas em segundos — sobre saúde, educação, programação, planos de viagem, idiomas, dicas gerais e muito mais.

- 🌤️ **Previsão do Tempo:**  
  Receba atualizações do clima locais e personalizadas com base em sua localização atual.

- 🔍 **Pesquisar na Web:**  
  Inclui integração com Google Search e navegação direta por links.

- 📄 **Resumo de Páginas Web:**  
  Cole uma URL e receba um resumo inteligente da página.

---

## ⚡ Guia Rápido: Como Rodar o Projeto

Siga estes passos simples para executar o OmniIA no seu ambiente local:

---

### 1. 📦 Pré-requisitos Essenciais

- **Python**: Certifique-se de ter o **Python 3.8 ou superior** instalado.
- **Ambiente Virtual**: Recomendado usar um ambiente virtual para evitar conflitos de dependência.

---

### 2. ⚙️ Prepare seu Projeto

No terminal, execute:

```bash
git clone https://github.com/seu-usuario/OmniIA.git
cd OmniIA
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

---

### 3. 🔐 Configure suas Credenciais

Crie o arquivo `secrets.toml` no caminho:

```
.streamlit/secrets.toml
```

Exemplo de estrutura:

```toml
# OpenAI API Key
OPENAI_API_KEY = "sua_chave_openai"

# WeatherAPI Key
WEATHERAPI_KEY = "sua_chave_weatherapi"

# URL do TogetherAI (se estiver usando)
TOGETHER_API_KEY = "sua_chave_togetherai"
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
```

---

### 4. 🧠 Execute o Projeto

```bash
streamlit run app.py
```

Acesse no navegador:  
📍 `http://localhost:8501`

---

## ☁️ Implantação na Nuvem (Opcional)

Você pode subir este projeto para a **Streamlit Cloud**.

1. Faça o push do projeto para seu GitHub
2. Acesse [streamlit.io/cloud](https://streamlit.io/cloud)
3. Siga as instruções para conectar seu repositório
4. Configure o `secrets.toml` diretamente na interface da Streamlit Cloud

---

## 🛠️ Dicas e Possíveis Problemas

- **Erros com PDF:** Se ocorrer erro ao ler arquivos PDF, verifique permissões ou formato.
- **Chave da API inválida:** Revise seu arquivo `secrets.toml`.

---

## 📄 Licença

Este projeto está sob a licença **MIT**.