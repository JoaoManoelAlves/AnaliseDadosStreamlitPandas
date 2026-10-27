import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Análise de Dados de Online Rentail",
    layout="wide"
)

@st.cache_data
def carregar_csv(arquivo):
    df = pd.read_csv(arquivo)
    return df

with st.sidebar:
    st.header("Carregador de dados")

    planilha = st.file_uploader(
        "Selecione uma planilha",
        type=["xlsx", "xls", "csv"]
    )

    carregar = st.button("Carregar planilha", type="primary")
    
    st.write("Online Rentail")
    st.markdown("Link: [Online Rentail](https://archive.ics.uci.edu/dataset/352/online+retail)")
    st.markdown('Referência: [Chen, Daqing. "Online Retail." UCI Machine Learning Repository, 2015](https://doi.org/10.24432/C5BW33).')
    st.write("Analistas de dados: João Manoel e Kaio Javã")

st.title("**Por que analisar esse database?**")
st.write("O objetivo da análise é identificar padrões de vendas e comportamento dos clientes do varejo online sem loja física, registrado e sediado no UK(Reino Unido), analisando o faturamento, os produtos mais vendidos, a frequência de compra e o perfil dos consumidores, a fim de gerar informações que auxiliem na tomada de decisões estratégicas e na melhoria dos resultados do negócio.")

if carregar:
    if planilha is not None:
        try:
            if planilha.name.endswith(".csv"):
                df = carregar_csv(planilha)
            st.session_state["df"] = df
            st.success("Planilha carregada com sucesso!")
            st.subheader("Prévia dos dados")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Erro ao carregar a planilha: {e}")
    else:
        st.warning("Selecione uma planilha primeiro.")
st.divider()
st.subheader("Selecione a quantidade de produtos que as pessoas compram")
if "df" in st.session_state:
    quantidade_produtos = st.slider(label="Quantidade de produtos", min_value=1, max_value=150)
    df = st.session_state["df"]
    df_filtrado = df[df["Quantity"] >= quantidade_produtos]
    
    st.subheader("Quantidade de produtos comprados na planilha")
    st.dataframe(df_filtrado, use_container_width=True)
    st.caption(
        f"Exibindo {len(df_filtrado)} "
        f"de {len(df)} registros."
    )
else:
    st.info("Carregue uma planilha na barra lateral para visualizar os dados.")
st.divider()
st.write("<h2>Selecione o país de compra</h2>", unsafe_allow_html=True)
if "df" in st.session_state:
    df = st.session_state["df"]
    paises = sorted(df["Country"].dropna().unique().tolist())
    paises_selecionados = st.multiselect(label="Selecione os países", options=paises, default=paises)

    df_filtrado = df[df["Country"].isin(paises_selecionados)]

    total = len(df)
    exibidos = len(df_filtrado)

    st.subheader("Registros filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

    st.caption(
        f"Exibindo {exibidos} de {total} registros "
    )
else:
    st.info("Carregue uma planilha para utilizar os filtros.")

st.divider()
st.subheader("Dicionário de Dados e Amostragem")
if "df" in st.session_state:
    df = st.session_state["df"]

    aba1, = st.tabs(["Dicionário de Dados e Amostragem"])

    with aba1:
        st.header("Dicionário de Dados e Amostragem")

        # 1. Dicionário de dados
        st.subheader("1. Dicionário de dados")

        dicionario = {
            "InvoiceNo": {
                "Significado": "Identificador da fatura",
                "Unidade": "Código",
                "Tipo": "Qualitativa nominal"
            },
            "StockCode": {
                "Significado": "Código identificador do produto",
                "Unidade": "Código",
                "Tipo": "Qualitativa nominal"
            },
            "Description": {
                "Significado": "Descrição do produto",
                "Unidade": "Texto",
                "Tipo": "Qualitativa nominal"
            },
            "Quantity": {
                "Significado": "Quantidade de itens comprados",
                "Unidade": "Unidades",
                "Tipo": "Quantitativa discreta"
            },
            "InvoiceDate": {
                "Significado": "Data e hora da transação",
                "Unidade": "Data/hora",
                "Tipo": "Temporal"
            },
            "UnitPrice": {
                "Significado": "Preço por unidade do produto",
                "Unidade": "Libras esterlinas (£)",
                "Tipo": "Quantitativa contínua"
            },
            "CustomerID": {
                "Significado": "Identificador do cliente",
                "Unidade": "Código",
                "Tipo": "Qualitativa nominal"
            },
            "Country": {
                "Significado": "País associado à transação",
                "Unidade": "País",
                "Tipo": "Qualitativa nominal"
            }
        }

        # Exibe apenas as colunas existentes no arquivo
        linhas_dicionario = []

        for coluna in df.columns:
            if coluna in dicionario:
                linhas_dicionario.append({
                    "Coluna": coluna,
                    **dicionario[coluna]
                })
            else:
                linhas_dicionario.append({
                    "Coluna": coluna,
                    "Significado": "Significado não documentado",
                    "Unidade": "Não definida",
                    "Tipo": str(df[coluna].dtype)
                })

        df_dicionario = pd.DataFrame(linhas_dicionario)
        st.dataframe(df_dicionario, use_container_width=True, hide_index=True)

        st.divider()

        # 2. Relatório de sanidade
        st.subheader("2. Relatório de sanidade dos dados")

        valores_ausentes = int(df.isna().sum().sum())
        linhas_duplicadas = int(df.duplicated().sum())

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Linhas totais", len(df))

        with col2:
            st.metric("Valores ausentes (NaN)", valores_ausentes)

        with col3:
            st.metric("Linhas duplicadas", linhas_duplicadas)

        st.write("**Valores ausentes por coluna**")

        ausentes_por_coluna = (
            df.isna()
            .sum()
            .rename("Valores ausentes")
            .reset_index()
        )
        ausentes_por_coluna.columns = ["Coluna", "Valores ausentes"]

        st.dataframe(
            ausentes_por_coluna,
            use_container_width=True,
            hide_index=True
        )

        st.info(
            "Este relatório é diagnóstico: contabiliza valores ausentes "
            "e duplicatas sem alterar o DataFrame original."
        )

        st.divider()

        # 3. Amostragem
        st.subheader("3. Visualização da amostra")

        quantidade_linhas = st.slider(
            "Quantidade de linhas para visualizar",
            min_value=1,
            max_value=max(1, len(df)),
            value=min(10, max(1, len(df)))
        )

        st.dataframe(
            df.head(quantidade_linhas),
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            f"Exibindo {min(quantidade_linhas, len(df))} "
            f"de {len(df)} linhas."
        )

else:
    st.info("Carregue a planilha na barra lateral para visualizar esta aba.")
