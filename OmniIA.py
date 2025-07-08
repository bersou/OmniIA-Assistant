import streamlit as st
import requests

# 🔑 Lendo chaves do arquivo secrets.toml
WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

st.set_page_config(page_title="OmniIA Assistant", page_icon="🧠", layout="centered")
st.markdown("<h1 style='color: green;'>🧠 OmniIA Assistant</h1>", unsafe_allow_html=True)

# ------------------------------
# 🌤️ Previsão do tempo - OpenWeather
# ------------------------------
st.subheader("Previsão do Tempo")
cidade = st.text_input("Digite o nome da cidade")

if st.button("Buscar clima") and cidade:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={WEATHER_API_KEY}&units=metric&lang=pt_br"

    try:
        resposta = requests.get(url)
        dados = resposta.json()

        if resposta.status_code == 401:
            st.error("❌ Chave de API inválida para OpenWeather.")
        elif resposta.status_code == 404:
            st.warning("⚠️ Cidade não encontrada. Verifique o nome digitado.")
        elif resposta.status_code != 200:
            st.error("⚠️ Erro ao acessar a API do tempo.")
        else:
            temp = dados["main"]["temp"]
            descricao = dados["weather"][0]["description"]
            umidade = dados["main"]["humidity"]
            vento = dados["wind"]["speed"]

            st.success(f"🌤️ Clima em **{cidade.title()}**:")
            st.write(f"**Temperatura:** {temp}°C")
            st.write(f"**Descrição:** {descricao.capitalize()}")
            st.write(f"**Umidade:** {umidade}%")
            st.write(f"**Vento:** {vento} m/s")

    except Exception as e:
        st.error(f"Erro inesperado: {e}")

# ------------------------------
# 🔎 Pesquisa Web (Simulada)
# ------------------------------
st.subheader("Pesquisa Web (Simulação)")
consulta = st.text_input("Digite o que deseja pesquisar na web")

if st.button("Pesquisar"):
    st.info("🔐 Simulação: chave fictícia da SerpAPI. Nenhuma pesquisa real será feita.")

# ------------------------------
# 🤖 Assistente IA (Gemini - Simulado)
# ------------------------------
st.subheader("Assistente IA (Simulado)")
pergunta = st.text_area("Digite sua pergunta para a IA")

if st.button("Perguntar à IA"):
    st.info("💡 Simulação: chave fictícia do Gemini. Nenhuma resposta real será gerada.")