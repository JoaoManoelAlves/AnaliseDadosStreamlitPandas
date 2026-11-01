"""
secoes/aba_dicionario.py  —  ABA 1: dicionário de dados e amostragem
====================================================================
 1) Dicionário (significado, unidade, tipo de cada coluna)
 2) Relatório de sanidade (nulos e duplicadas)
 3) Amostra da base com slider de quantidade de linhas
"""
import pandas as pd
import streamlit as st

from dados import montar_dicionario


def renderizar(df_completo: pd.DataFrame, df_filtrado: pd.DataFrame, relatorio: dict):
    # ---- 1) Dicionário de dados --------------------------------------------
    st.subheader("📖 Dicionário de dados")
    st.caption(
        "Cada linha da base representa **um dia** de operação do sistema "
        "Capital Bikeshare (Washington, D.C.), entre 2011 e 2012."
    )
    st.dataframe(montar_dicionario(df_completo), hide_index=True)
    st.caption(
        "Observação: temperatura, sensação térmica, umidade e vento chegam "
        "normalizados (0 a 1) da UCI; foram convertidos para unidades reais "
        "(fórmulas na coluna *Significado*). A coluna `instant` (índice) foi descartada."
    )

    # ---- 2) Relatório de sanidade -------------------------------------------
    st.subheader("🩺 Relatório de sanidade da base")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Linhas originais", relatorio["linhas_originais"])
    c2.metric("Valores ausentes (NaN) tratados", relatorio["total_nulos"])
    c3.metric("Linhas duplicadas removidas", relatorio["duplicadas"])
    c4.metric("Linhas após o tratamento", relatorio["linhas_finais"])

    if relatorio["total_nulos"] == 0 and relatorio["duplicadas"] == 0:
        st.success("A base chegou limpa: nenhum valor ausente e nenhuma linha duplicada.")
    else:
        st.warning("Foram encontrados problemas, tratados conforme a regra abaixo.")
        if relatorio["total_nulos"] > 0:
            st.write("Valores ausentes por coluna (antes do tratamento):")
            st.dataframe(relatorio["nulos_por_coluna"].rename("nulos").to_frame())

    with st.expander("Como o tratamento é feito"):
        st.markdown(
            "- **Duplicadas:** removidas com `drop_duplicates()`.\n"
            "- **Datas inválidas:** linhas descartadas.\n"
            "- **Nulos em códigos categóricos:** preenchidos com a **moda**.\n"
            "- **Nulos em medidas numéricas:** preenchidos com a **mediana** "
            "(robusta a outliers).\n"
            "- **Consistência:** `total_alugueis` é conferido contra "
            "`usuarios_casuais + usuarios_registrados`."
        )

    # ---- 3) Amostra da base ---------------------------------------------------
    st.subheader("🔎 Amostra dos dados (respeita os filtros da barra lateral)")
    maximo = max(len(df_filtrado), 1)
    limite = min(maximo, 100)
    n = st.slider(
        "Quantidade de linhas a exibir",
        min_value=1,
        max_value=max(limite, 2),   # o slider exige min < max
        value=min(10, limite),
        key="amostra_n",
    )
    st.dataframe(df_filtrado.head(n), hide_index=True)
