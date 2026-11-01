"""
app.py  —  ponto de entrada do dashboard (BLOCO 0)
==================================================
Este arquivo só ORQUESTRA: configura a página, carrega os dados, monta a barra
lateral e distribui o conteúdo pelas abas. A lógica de cada parte mora em módulos:

    config.py               constantes, caminhos, rótulos
    dados.py                leitura (com cache), higienização, dicionário
    estatistica.py          cálculos (média, IQR, Tukey, Pearson...)
    secoes/barra_lateral.py Bloco 1: identificação + filtros + contador
    secoes/aba_dicionario.py  Aba 1
    secoes/aba_univariada.py  Aba 2
    secoes/aba_bivariada.py   Aba 3
    secoes/aba_parecer.py     Aba 4

Execução:  streamlit run app.py
"""
import streamlit as st

import config
from dados import carregar_dados
from secoes import aba_bivariada, aba_dicionario, aba_parecer, aba_univariada, barra_lateral

# ---- Bloco 0: configuração da página (deve ser a 1ª chamada do Streamlit) ----------
st.set_page_config(
    page_title="Bike Sharing — Estatística Descritiva",
    page_icon="🚲",
    layout="wide",
)

st.title("🚲 Dashboard de Estatística Descritiva — Bike Sharing (UCI)")
st.caption("IFMA · TSI · Tópicos Especiais em Programação / Análise de Dados")

# ---- Bloco 0: carregamento dos dados (função com @st.cache_data) -------------------------
if not config.CAMINHO_CSV.exists():
    st.error(
        f"Arquivo **{config.CAMINHO_CSV.name}** não encontrado na pasta `database/`.\n\n"
        f"Baixe a base em {config.LINK_UCI}, extraia o .zip e copie o `day.csv` "
        "para a pasta `database/`."
    )
    st.stop()

df, relatorio = carregar_dados(str(config.CAMINHO_CSV))

# ---- Bloco 1: barra lateral (devolve o DataFrame já filtrado) ----------------------------
df_filtrado = barra_lateral.renderizar(df)

if df_filtrado.empty:
    st.warning("Os filtros atuais não retornaram nenhum registro. Amplie a seleção na barra lateral.")
    st.stop()

# ---- Bloco 2: navegação em abas --------------------------------------------------------------
aba1, aba2, aba3, aba4 = st.tabs([
    "📖 Dicionário e amostragem",
    "📊 Univariada e outliers",
    "🔗 Bivariada e correlação",
    "📝 Parecer analítico",
])

with aba1:
    aba_dicionario.renderizar(df, df_filtrado, relatorio)
with aba2:
    aba_univariada.renderizar(df_filtrado)
with aba3:
    aba_bivariada.renderizar(df_filtrado)
with aba4:
    aba_parecer.renderizar(df_filtrado)