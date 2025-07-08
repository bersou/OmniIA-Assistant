import os
import json
import datetime
import streamlit as st
import requests

# ========== CONFIGURAÇÃO DE LIMITES ==========
LIMITES_DIARIOS = {
    "gemini": 50,
    "openweather": 20,
    "serpapi": 30
}

USO_PATH = "uso.json"

# ========== FUNÇÕES DE CONTROLE DE USO ==========

def carregar_uso():
    if not os.path.exists(USO_PATH):
        return {"data": str(datetime.date.today()), "contadores": {api: 0 for api in LIMITES_DIARIOS}}

    with open(USO_PATH, "r") as f:
        uso = json.load(f)

    # Se for um novo dia, zera os contadores
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

# ========== EXEMPLO DE USO DAS APIS ==========

# --- Gemini (via LangChain, etc.)
def chamar_gemini(prompt):
    if not pode_usar_api("gemini"):
        return "⚠️ Limite diário da API Gemini atingido."

    # Código real da chamada à API Gemini aqui
    return f"Resposta da IA (Gemini) para: {prompt}"

# --- OpenWeather
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

# --- SerpAPI
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

# ========== EXEMPLO STREAMLIT ==========

st.title("🌐 OmniIA Assistant com Controle de Uso de APIs")

aba = st.selectbox("Escolha uma função", ["IA (Gemini)", "Previsão do Tempo", "Pesquisa Web"])

if aba == "IA (Gemini)":
    prompt = st.text_input("Digite sua pergunta para a IA")
    if st.button("Enviar"):
        resposta = chamar_gemini(prompt)
        st.write(resposta)

elif aba == "Previsão do Tempo":
    cidade = st.text_input("Digite o nome da cidade")
    OPENWEATHER_KEY = st.secrets["openweather_key"]
    if st.button("Buscar clima"):
        clima = obter_clima(cidade, OPENWEATHER_KEY)
        st.write(clima)

elif aba == "Pesquisa Web":
    termo = st.text_input("Digite o termo de pesquisa")
    SERPAPI_KEY = st.secrets["serpapi_key"]
    if st.button("Pesquisar"):
        resultado = buscar_web_serpapi(termo, SERPAPI_KEY)
        st.write(resultado)