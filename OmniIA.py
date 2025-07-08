import os
import requests
import re
import streamlit as st
from bs4 import BeautifulSoup
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional, List
from io import BytesIO
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from datetime import datetime

# --- Configurações ---
MAX_REQUESTS_PER_DAY = 50

# --- Chaves de API ---
WEATHER_API_KEY = st.secrets.get("WEATHER_API_KEY", "")
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", "")
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")

# --- Verificação de limite de uso ---
def verificar_limite():
    hoje = datetime.now().date()
    if "uso_modelo_data" not in st.session_state:
        st.session_state.uso_modelo_data = hoje
        st.session_state.uso_modelo_count = 0
    elif st.session_state.uso_modelo_data != hoje:
        st.session_state.uso_modelo_data = hoje
        st.session_state.uso_modelo_count = 0
    return st.session_state.uso_modelo_count < MAX_REQUESTS_PER_DAY

def registrar_uso():
    st.session_state.uso_modelo_count += 1

# --- Instância do modelo ---
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7,
    max_output_tokens=1024
)

# --- Funções ---

def perguntar(user_message_content: str) -> str:
    if not verificar_limite():
        return "**⚠️ Limite de uso diário do modelo atingido. Tente novamente amanhã.**"

    system_instruction = """Você é um assistente de IA prestativo e profissional.
    Responda em português de forma clara e útil.
    Use **blocos de código Markdown (` ``` `)** para exemplos de código.
    Use **negrito** para destacar palavras importantes.
    Seja direto e conciso. Não revele métodos internos.
    """
    full_messages = [SystemMessage(content=system_instruction)]

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            full_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            full_messages.append(AIMessage(content=msg["content"]))

    full_messages.append(HumanMessage(content=user_message_content))

    resposta = llm.invoke(full_messages).content
    registrar_uso()
    return resposta


def previsao_tempo(cidade: str) -> str:
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={cidade}&lang=pt"
        resposta = requests.get(url).json()
        if "error" in resposta:
            return f"Erro: {resposta['error'].get('message', 'Erro desconhecido')}"
        clima = resposta["current"]["condition"]["text"]
        temp = resposta["current"]["temp_c"]
        sensacao = resposta["current"]["feelslike_c"]
        umidade = resposta["current"]["humidity"]
        vento = resposta["current"]["wind_kph"]
        return f"**{cidade}**\n- Clima: {clima}\n- Temperatura: {temp:.1f}°C\n- Sensação térmica: {sensacao:.1f}°C\n- Umidade: {umidade}%\n- Vento: {vento} km/h"
    except Exception as e:
        return f"Erro ao buscar previsão do tempo: {e}"

def pesquisar_web(termo: str, max_links: int = 5) -> List[str]:
    try:
        params = {
            "engine": "google",
            "q": termo,
            "api_key": SERPAPI_KEY
        }
        resposta = requests.get("https://serpapi.com/search", params=params).json()
        resultados = resposta.get("organic_results", [])
        links = [res.get("link") for res in resultados if res.get("link")][:max_links]
        return links if links else ["Nenhum resultado encontrado."]
    except Exception as e:
        return [f"Erro: {e}"]

def resumir_pagina_web(url: str) -> str:
    try:
        if not verificar_limite():
            return "**⚠️ Limite de uso diário do modelo atingido. Tente novamente amanhã.**"

        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        if len(text) > 4000:
            text = text[:4000] + "..."

        prompt = f"Por favor, resuma o seguinte conteúdo de uma página web de forma concisa e clara em português:\n\n{text}\n\nResumo:"
        registrar_uso()
        return llm.invoke(prompt).content
    except requests.exceptions.RequestException as e:
        return f"Erro ao acessar a URL: {e}. Por favor, verifique se a URL está correta e é acessível."
    except Exception as e:
        return f"Ocorreu um erro ao processar a página: {e}"


# --- Interface com Streamlit ---
st.set_page_config(page_title="OmniIA: Inteligência Integrada", layout="centered")

st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <h1 style='color: #3a7bd5;'>🤖 OmniIA</h1>
        <h3 style='color: gray;'>Inteligência Integrada para suas tarefas diárias</h3>
    </div>
    <hr style='margin-bottom: 2rem;'>
""", unsafe_allow_html=True)

if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "Perguntar"
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("## Peça ao OmniIA")

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

# --- Modos de uso ---

if st.session_state.current_mode == "Perguntar":
    st.markdown("## 💬 Chat com o OmniIA")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Digite sua mensagem aqui...", key="chat_input_main"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = perguntar(prompt)

                if "```" in response:
                    padrao_codigo = r"```(?:\w*\n)?([\s\S]+?)```"
                    trechos = re.findall(padrao_codigo, response)

                    if trechos:
                        for trecho in trechos:
                            st.code(trecho, language="python")
                            st.text_area("Clique e copie:", value=trecho, height=100)

                    explicacao = re.sub(padrao_codigo, "", response).strip()
                    if explicacao:
                        st.markdown(explicacao)
                else:
                    st.markdown(response)

                st.session_state.messages.append({"role": "assistant", "content": response})


elif st.session_state.current_mode == "PrevisaoTempo":
    st.markdown("## ☁️ Previsão do Tempo")
    cidade = st.text_input("Digite a cidade", "Gravataí", key="weather_city_input")
    if st.button("Consultar Previsão", key="btn_consult_weather"):
        with st.spinner("Buscando previsão..."):
            resultado = previsao_tempo(cidade)
            st.markdown(resultado)

elif st.session_state.current_mode == "PesquisarWeb":
    st.markdown("## 🌐 Pesquisar na Web")
    termo = st.text_input("Buscar por:", value="", key="web_search_term_input")
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
    url_input = st.text_input("Insira a URL da página para resumir:", key="page_summary_url_input")
    if st.button("Gerar Resumo da Página", key="btn_generate_page_summary") and url_input:
        with st.spinner("Buscando e resumindo a página..."):
            resumo = resumir_pagina_web(url_input)
            st.markdown("### Resumo:")
            st.write(resumo)