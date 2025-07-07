import os
import requests
import re
import streamlit as st
from bs4 import BeautifulSoup
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional, List
from io import BytesIO

# Importações para memória de sessão
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# --- Configurações Iniciais ---
# Chaves de API
OPENWEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY", "")
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", "")
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")

# Instância do LLM usando Google Gemini 1.5 Flash
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7,
    max_output_tokens=1024
)

# Funções utilitárias

# Função perguntar: instrução do sistema aprimorada para formatação e memória


def perguntar(user_message_content: str) -> str:
    system_instruction = """Você é um assistente de IA prestativo e profissional.
    Responda em português de forma clara e útil.
    Quando fornecer código, comandos, passos de tutorial, nomes de arquivos, ou trechos de texto importantes para copiar, use **blocos de código Markdown (` ```)**.
    Para destacar termos importantes ou palavras-chave em uma frase, use **negrito (`**texto**`)**.
    Sempre busque ser conciso(a) e direto(a) ao ponto.
    Se a pergunta for um pedido simples que não necessita de tutorial/código, responda normalmente.
    """
    full_messages = [SystemMessage(content=system_instruction)]

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            full_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            full_messages.append(AIMessage(content=msg["content"]))

    full_messages.append(HumanMessage(content=user_message_content))

    response_obj = llm.invoke(full_messages).content
    return response_obj


def previsao_tempo(cidade: str) -> str:
    try:
        # URL corrigido (removida formatação Markdown)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt"
        resposta = requests.get(url).json()
        if resposta.get("cod") != 200:
            return f"Erro: {resposta.get('message', 'Erro desconhecido')}"
        clima = resposta["weather"][0]["description"].capitalize()
        temp = resposta["main"]["temp"]
        sensacao = resposta["main"]["feels_like"]
        umidade = resposta["main"]["humidity"]
        vento = resposta["wind"]["speed"]
        return f"**{cidade}**\n- Clima: {clima}\n- Temperatura: {temp:.1f}°C\n- Sensação térmica: {sensacao:.1f}°C\n- Umidade: {umidade}%\n- Vento: {vento} m/s"
    except Exception as e:
        return f"Erro ao buscar previsão do tempo: {e}"


def pesquisar_web(termo: str, max_links: int = 5) -> List[str]:
    try:
        params = {
            "engine": "google",
            "q": termo,
            "api_key": SERPAPI_KEY
        }
        # URL corrigido (removida formatação Markdown)
        resposta = requests.get(
            "https://serpapi.com/search", params=params).json()
        resultados = resposta.get("organic_results", [])
        links = [res.get("link")
                 for res in resultados if res.get("link")][:max_links]
        return links if links else ["Nenhum resultado encontrado."]
    except Exception as e:
        return [f"Erro: {e}"]


def resumir_pagina_web(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip()
                  for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        if len(text) > 4000:
            text = text[:4000] + "..."

        prompt = f"Por favor, resuma o seguinte conteúdo de uma página web de forma concisa e clara em português:\n\n{text}\n\nResumo:"
        return llm.invoke(prompt).content
    except requests.exceptions.RequestException as e:
        return f"Erro ao acessar a URL: {e}. Por favor, verifique se a URL está correta e é acessível."
    except Exception as e:
        return f"Ocorreu um erro ao processar a página: {e}"


# --- Função para adicionar botões de cópia aos blocos de código ---
def add_copy_buttons_to_markdown(markdown_text: str) -> str:
    # JavaScript para copiar o texto e mostrar feedback
    js_code = """
    <script>
    function copyCode(buttonElement) {
        // Encontra o elemento de código (pre-code) que precede o botão
        var codeBlockContainer = buttonElement.parentElement;
        var codeBlock = codeBlockContainer.querySelector('code');
        
        if (!codeBlock) {
            console.error("Elemento de código não encontrado.");
            return;
        }
        var textToCopy = codeBlock.innerText;
        
        var textArea = document.createElement("textarea");
        textArea.value = textToCopy;
        textArea.style.position = "fixed"; // Evita rolagem
        textArea.style.left = "-9999px"; // Fora da tela
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            var successful = document.execCommand('copy');
            var msg = successful ? 'Copiado!' : 'Falha ao copiar.';
            var feedbackSpan = buttonElement.nextElementSibling;
            if (feedbackSpan && feedbackSpan.classList.contains('copy-feedback')) {
                feedbackSpan.innerText = msg;
                feedbackSpan.style.opacity = 1;
                setTimeout(function() {
                    feedbackSpan.style.opacity = 0;
                }, 2000);
            }
        } catch (err) {
            console.error('Erro ao copiar: ', err);
        }
        document.body.removeChild(textArea);
    }
    </script>
    """

    # Regex para encontrar blocos de código Markdown
    # Captura o idioma (opcional) e o conteúdo do código
    def replace_code_block(match):
        lang = match.group(1) if match.group(1) else ''
        code_content = match.group(2)
        # Escapa caracteres HTML dentro do código para evitar quebras
        escaped_code_content = code_content.replace(
            '&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # Estrutura HTML com botão de copiar
        return f"""
<div style="position: relative; background-color: #262730; padding: 10px; border-radius: 8px; margin-bottom: 15px; overflow-x: auto;">
    <pre style="margin: 0; padding-right: 60px;"><code class="language-{lang}">{escaped_code_content}</code></pre>
    <button onclick="copyCode(this)" style="position: absolute; top: 10px; right: 10px; background-color: #007bff; color: white; border: none; border-radius: 5px; padding: 6px 12px; cursor: pointer; font-size: 0.85em; transition: background-color 0.2s ease;">Copiar</button>
    <span class="copy-feedback" style="position: absolute; top: 10px; right: 80px; color: #4CAF50; font-size: 0.8em; opacity: 0; transition: opacity 0.3s ease-in-out; background-color: rgba(255, 255, 255, 0.9); padding: 3px 6px; border-radius: 3px; white-space: nowrap;"></span>
</div>
"""

    # Substitui todos os blocos de código Markdown pela estrutura HTML com botão
    # Usa re.DOTALL para que '.' inclua novas linhas
    processed_text = re.sub(r'```(\w*)\n(.*?)```',
                            replace_code_block, markdown_text, flags=re.DOTALL)

    # Adiciona o script JS no final do texto processado, garantindo que seja injetado uma vez
    # Streamlit executará este script quando o markdown for renderizado.
    return processed_text + js_code


# --- Interface com Streamlit - Customização visual ---
st.set_page_config(
    page_title="OmniIA: Inteligência Integrada", layout="centered")
st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <h1 style='color: #3a7bd5;'>🤖 OmniIA</h1>
        <h3 style='color: gray;'>Inteligência Integrada para suas tarefas diárias</h3>
    </div>
    <hr style='margin-bottom: 2rem;'>
""", unsafe_allow_html=True)

# Inicializar estado da sessão
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "Perguntar"
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Título principal no topo ---
st.markdown("## Peça ao OmniIA")


# --- Botões de Ação para Ferramentas ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### Selecione uma Ferramenta ou Ação:")

cols_buttons = st.columns(4)

with cols_buttons[0]:
    if st.button("💬 Chat (IA Geral)", key="btn_chat_general"):
        st.session_state.current_mode = "Perguntar"

with cols_buttons[1]:
    if st.button("☁️ Previsão do Tempo", key="btn_weather"):
        st.session_state.current_mode = "PrevisaoTempo"

with cols_buttons[2]:
    if st.button("🌐 Pesquisar na Web", key="btn_web_search"):
        st.session_state.current_mode = "PesquisarWeb"

with cols_buttons[3]:
    if st.button("📄 Resumir Página", key="btn_page_summary"):
        st.session_state.current_mode = "ResumirPagina"

st.markdown("---")


# --- Seções Específicas de Ferramentas (aparecem de acordo com o current_mode) ---

if st.session_state.current_mode == "Perguntar":
    st.markdown("## 💬 Chat com o OmniIA")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Use a função para adicionar botões de cópia ao exibir mensagens do assistente
            if message["role"] == "assistant":
                st.markdown(add_copy_buttons_to_markdown(
                    message["content"]), unsafe_allow_html=True)
            else:
                st.markdown(message["content"])

    if prompt := st.chat_input("Digite sua mensagem aqui...", key="chat_input_main"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = perguntar(prompt)
                # Adicione a resposta bruta à sessão para manter a memória
                st.session_state.messages.append(
                    {"role": "assistant", "content": response})
                # Exiba a resposta processada com botões de cópia
                st.markdown(add_copy_buttons_to_markdown(
                    response), unsafe_allow_html=True)

elif st.session_state.current_mode == "PrevisaoTempo":
    st.markdown("## ☁️ Previsão do Tempo")
    cidade = st.text_input("Digite a cidade", "Gravataí",
                           key="weather_city_input")
    if st.button("Consultar Previsão", key="btn_consult_weather"):
        with st.spinner("Buscando previsão..."):
            resultado = previsao_tempo(cidade)
            st.markdown(resultado)

elif st.session_state.current_mode == "PesquisarWeb":
    st.markdown("## 🌐 Pesquisar na Web")
    st.write("Digite seu termo de busca.")

    termo = st.text_input(
        "Buscar por:",
        value="",
        key="web_search_term_input"
    )

    if st.button("Pesquisar na Web", key="btn_perform_web_search"):
        if termo:
            with st.spinner("Pesquisando na web..."):
                resultados = pesquisar_web(termo)
                for i, link in enumerate(resultados, 1):
                    st.markdown(f"{i}. [{link}]({link})")
        else:
            st.warning("Por favor, digite um termo para pesquisar.")

elif st.session_state.current_mode == "ResumirPagina":
    st.markdown("## 📄 Resumo de Páginas Web")
    url_input = st.text_input(
        "Insira a URL da página para resumir:", key="page_summary_url_input")
    if st.button("Gerar Resumo da Página", key="btn_generate_page_summary") and url_input:
        with st.spinner("Buscando e resumindo a página..."):
            resumo = resumir_pagina_web(url_input)
            st.markdown("### Resumo:")
            st.write(resumo)
