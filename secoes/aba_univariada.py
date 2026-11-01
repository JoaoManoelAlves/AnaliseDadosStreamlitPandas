"""
secoes/aba_univariada.py  —  ABA 2: estatística univariada e outliers
=====================================================================
Para a variável escolhida: cartões (média, mediana, desvio, IQR), tabela
describe(), diagnóstico de assimetria, histograma com bins ajustáveis,
boxplot e detecção de outliers pelo critério de Tukey (1,5 × IQR).
"""
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import config
import estatistica as est
from estatistica import fmt_num


def renderizar(df: pd.DataFrame):
    st.subheader("📊 Estatística descritiva univariada e outliers")

    variavel = st.selectbox(
        "Escolha a variável numérica",
        options=config.COLUNAS_NUMERICAS,
        format_func=lambda c: config.ROTULOS[c],
        index=config.COLUNAS_NUMERICAS.index("total_alugueis"),
        key="uni_variavel",
    )
    serie = df[variavel].dropna()
    rotulo = config.ROTULOS[variavel]

    if len(serie) < 2:
        st.warning("Poucos registros após os filtros para calcular as estatísticas.")
        return

    r = est.resumo_univariado(serie)

    # ---- Cartões de métricas ----------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Média", fmt_num(r["media"]))
    c2.metric("Mediana", fmt_num(r["mediana"]))
    c3.metric("Desvio padrão", fmt_num(r["desvio"]))
    c4.metric("IQR (Q3 − Q1)", fmt_num(r["iqr"]))

    # ---- Tabela describe() ----------------------------------------------------------
    st.markdown("**Resumo estatístico (`describe()`)**")
    st.dataframe(df[[variavel]].describe().T.round(2))
    with st.expander("Ver `describe()` de todas as variáveis numéricas"):
        st.dataframe(df[config.COLUNAS_NUMERICAS].describe().T.round(2))

    # ---- Diagnóstico de assimetria -----------------------------------------------------
    rotulo_assim, explicacao, recomendada = est.diagnostico_assimetria(
        r["media"], r["mediana"], r["desvio"]
    )
    st.info(
        f"**🩺 Diagnóstico de assimetria:** {rotulo_assim}\n\n"
        f"{explicacao}\n\n"
        f"Coeficiente de assimetria (skew): **{fmt_num(r['assimetria'])}**\n\n"
        f"**Métrica central mais recomendada:** {recomendada}"
    )

    # ---- Outliers (Tukey) -------------------------------------------------------------------
    tk = est.limites_tukey(serie)

    # ---- Gráficos: histograma (com bins ajustáveis) + boxplot ---------------------------------
    bins = st.slider("Número de faixas (bins) do histograma", 5, 60, 20, key="uni_bins")
    g1, g2 = st.columns(2)

    with g1:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(serie, bins=bins, color="#4C78A8", edgecolor="white")
        ax.axvline(r["media"], color="#E45756", linestyle="-", label="Média")
        ax.axvline(r["mediana"], color="#54A24B", linestyle="--", label="Mediana")
        ax.axvline(tk["inferior"], color="gray", linestyle=":", label="Limites de Tukey")
        ax.axvline(tk["superior"], color="gray", linestyle=":")
        ax.set_title(f"Histograma — {rotulo}")
        ax.set_xlabel(rotulo)
        ax.set_ylabel("Frequência (dias)")
        ax.legend()
        st.pyplot(fig)
        plt.close(fig)

    with g2:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.boxplot(
            serie, vert=False, whis=1.5, patch_artist=True,
            boxprops={"facecolor": "#9ecae9"},
            flierprops={"markerfacecolor": "#E45756", "markeredgecolor": "#E45756"},
        )
        ax.set_title(f"Boxplot — {rotulo}")
        ax.set_xlabel(rotulo)
        ax.set_yticks([])
        st.pyplot(fig)
        plt.close(fig)

    st.markdown("**Detecção de outliers — critério de Tukey**")
    st.latex(r"LI = Q_1 - 1{,}5 \times IQR \qquad LS = Q_3 + 1{,}5 \times IQR")
    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Limite inferior", fmt_num(tk["inferior"]))
    o2.metric("Limite superior", fmt_num(tk["superior"]))
    o3.metric("Outliers detectados", tk["total"])
    o4.metric("% de outliers", f"{fmt_num(tk['percentual'], 1)}%")

    if tk["total"] == 0:
        st.success("Nenhum valor fora do intervalo de Tukey nesta variável.")
    else:
        with st.expander("Ver os dias considerados outliers"):
            cols = ["data", "estacao", "clima", variavel]
            st.dataframe(
                df.loc[tk["mascara"].reindex(df.index, fill_value=False), cols]
                .sort_values(variavel),
                hide_index=True,
            )
