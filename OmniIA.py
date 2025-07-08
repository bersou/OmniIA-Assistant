import os
import json
import datetime
import streamlit as st
import requests

# ========== CONFIGURAÇÃO ==========
st.set_page_config(page_title="OmniIA Assistant", layout="wide")

LIMITES_DIARIOS = {
    "gemini": 50,
    "openweather": 20,
    "serpapi": 30
}

USO_PATH = "uso.json"

# ========== CONTROLE DE USO ==========
def carregar_uso():
    if not os.path.exists(USO_PATH):
        return {"data": str(datetime.date.today()), "contadores": {api: 0 for api in LIMITES_DIARIOS}}
    with open(USO_PATH, "r") as f:
        uso = json.load(f)
    if uso["data"] != str(datetime.date.today()):
        uso = {"data": str(datetime.date.today()), "contadores": {api: 0 for api in LIMITES_DIARIOS}}
        salvar_uso(uso)
    return uso

def salvar_uso(uso):
    with open(USO_PATH, "w") as f:
        json.dump(uso, f)

def pode_usar_api(api_nome):
    uso = carregar_uso()
    if uso["contadores"][api_nome] < LIMITES_DIARIOS[api_nome]:
        uso["contadores"][api_nome] += 1
        salvar_uso(uso)
        return True
    else:
        return False

# ========== APIS ==========
def chamar_gemini(prompt):
    if not pode_usar_api("gemini"):
        return "⚠️ Limite diário da API Gemini atingido."
    # Aqui você colocaria a chamada real ao Gemini
    return f"Esta é uma resposta simulada da IA para: {prompt}"

def obter_clima(cidade, chave):
    if not pode_usar_api("openweather"):
        return "⚠️ Limite diário da API OpenWeather atingido."
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={chave}&lang=pt_br&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temp = data['main']['temp']
            desc = data['weather'][0]['description'].capitalize()
            return f"{cidade}: {temp}°C, {desc}"
        elif response.status_code == 401:
            return "❌ Chave de API inválida para OpenWeather."
        else:
            return f"Erro: {data.get('message', 'Erro ao buscar clima.')}"
    except Exception as e:
        return f"Erro na requisição: {e}"

def buscar_web_serpapi(consulta, chave):
    if not pode_usar_api("serpapi"):
        return "⚠️ Limite diário da API SerpAPI atingido."
    url = f"https://serpapi.com/search.json?q={consulta}&api_key={chave}&hl=pt-br&gl=br"
    try:
        resposta = requests.get(url)
        dados = resposta.json()
        if "error" in dados:
            return f"Erro: {dados['error']}"
        return dados
    except Exception as e:
        return f"Erro na busca web: {e}"

# ========== FUNÇÃO VISUAL: BLOCO COM COPIAR ==========
def bloco_com_copiar(titulo, conteudo):
    st.markdown(f"""
    <div style="position: relative; border: 1px solid #ddd; padding: 1em; border-radius: 10px; background-color: #f9f9f9;">
        <h4 style="margin-top: 0;">📄 {titulo}</h4>
        <pre id="blocoTexto" style="white-space: pre-wrap; word-wrap: break-word;">{conteudo}</pre>
        <button onclick="navigator.clipboard.writeText(document.getElementById('blocoTexto').innerText)" 
                style="position: absolute; top: 10px; right: 10px; padding: 5px 10px; border: none; background-color: #4CAF50; color: white; border-radius: 5px; cursor: pointer;">
            📋 Copiar
        </button>
    </div>
    """, unsafe_allow_html=True)

# ========== INTERFACE ==========
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🤖 OmniIA Assistant</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# Carregar dados de uso
uso = carregar_uso()
gemini_usado = uso["contadores"]["gemini"]
gemini_total = LIMITES_DIARIOS["gemini"]
percentual_gemini = gemini_usado / gemini_total

# Sidebar com controle e menu
with st.sidebar:
    st.header("⚙️ Menu")
    opcao = st.radio("Escolha a função:", ["IA (Gemini)", "Previsão do Tempo", "Pesquisa Web"])

    st.subheader("🔋 Uso da cota Gemini")
    st.progress(percentual_gemini)
    st.caption(f"{gemini_usado} de {gemini_total} requisições usadas hoje")

# Ações por aba
if opcao == "IA (Gemini)":
    prompt = st.text_input("Digite sua pergunta para a IA")
    if st.button("Enviar"):
        resposta = chamar_gemini(prompt)
        if len(resposta) > 80:
            bloco_com_copiar("Resposta da IA", resposta)
        else:
            st.success(resposta)

elif opcao == "Previsão do Tempo":
    cidade = st.text_input("Digite o nome da cidade")
    try:
        OPENWEATHER_KEY = st.secrets["openweather_key"]
        if st.button("Buscar clima"):
            clima = obter_clima(cidade, OPENWEATHER_KEY)
            st.info(clima)
    except Exception as e:
        st.error("Erro ao carregar chave da API OpenWeather.")

elif opcao == "Pesquisa Web":
    termo = st.text_input("Digite o termo de pesquisa")
    try:
        SERPAPI_KEY = st.secrets["serpapi_key"]
        if st.button("Pesquisar"):
            resultado = buscar_web_serpapi(termo, SERPAPI_KEY)
            if isinstance(resultado, dict):
                st.json(resultado)
            else:
                bloco_com_copiar("Resultado da pesquisa", str(resultado))
    except Exception as e:
        st.error("Erro ao carregar chave da API SerpAPI.")