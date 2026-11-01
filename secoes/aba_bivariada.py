"""
secoes/aba_bivariada.py  —  ABA 3: análise bivariada e correlação de Pearson
============================================================================
Gráfico de dispersão (eixos configuráveis, cor por categoria), coeficiente r
de Pearson com classificação, alerta de causalidade e matriz de correlação.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

import config
import estatistica as est
from estatistica import fmt_num


def _grafico_dispersao(df, x, y, cor, tendencia):
    fig, ax = plt.subplots(figsize=(8, 5))
    if cor == "(nenhuma)":
        ax.scatter(df[x], df[y], alpha=0.6, color="#4C78A8", edgecolor="white", linewidth=0.3)
    else:
        for categoria, grupo in df.groupby(cor):
            ax.scatter(grupo[x], grupo[y], alpha=0.65, label=str(categoria),
                       edgecolor="white", linewidth=0.3)
        ax.legend(title=config.ROTULOS[cor], fontsize=8)
    if tendencia and len(df) >= 3 and df[x].std() > 0:
        coef = np.polyfit(df[x], df[y], 1)           # reta de mínimos quadrados
        xs = np.linspace(df[x].min(), df[x].max(), 100)
        ax.plot(xs, coef[0] * xs + coef[1], color="black", linestyle="--")
    ax.set_xlabel(config.ROTULOS[x])
    ax.set_ylabel(config.ROTULOS[y])
    ax.set_title(f"{config.ROTULOS[y]} × {config.ROTULOS[x]}")
    ax.grid(alpha=0.2)
    return fig


def _mapa_de_calor(matriz: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(matriz.values, cmap="RdBu_r", vmin=-1, vmax=1)
    nomes = [config.ROTULOS[c].split(" (")[0] for c in matriz.columns]
    ax.set_xticks(range(len(nomes)))
    ax.set_yticks(range(len(nomes)))
    ax.set_xticklabels(nomes, rotation=45, ha="right")
    ax.set_yticklabels(nomes)
    for i in range(len(nomes)):
        for j in range(len(nomes)):
            valor = matriz.values[i, j]
            ax.text(j, i, f"{valor:.2f}", ha="center", va="center", fontsize=8,
                    color="white" if abs(valor) > 0.6 else "black")
    fig.colorbar(im, ax=ax, label="r de Pearson")
    ax.set_title("Matriz de correlação (Pearson)")
    fig.tight_layout()
    return fig


def renderizar(df: pd.DataFrame):
    st.subheader("🔗 Análise bivariada e correlação linear de Pearson")

    cols = config.COLUNAS_NUMERICAS
    c1, c2, c3 = st.columns(3)
    x = c1.selectbox("Eixo X", cols, index=cols.index("temp_c"),
                     format_func=lambda c: config.ROTULOS[c], key="bi_x")
    y = c2.selectbox("Eixo Y", cols, index=cols.index("total_alugueis"),
                     format_func=lambda c: config.ROTULOS[c], key="bi_y")
    cor = c3.selectbox("Colorir pontos por", ["(nenhuma)"] + config.COLUNAS_CATEGORICAS,
                       format_func=lambda c: config.ROTULOS.get(c, c), key="bi_cor")
    tendencia = st.checkbox("Mostrar reta de tendência linear", value=True, key="bi_tend")

    if len(df) < 3:
        st.warning("Poucos registros após os filtros para calcular a correlação.")
        return

    fig = _grafico_dispersao(df, x, y, cor, tendencia)
    st.pyplot(fig)
    plt.close(fig)

    # ---- Coeficiente r de Pearson ------------------------------------------------------
    st.markdown("**Coeficiente de correlação linear de Pearson**")
    if x == y:
        st.warning("X e Y são a mesma variável (r = 1 por definição). Escolha variáveis diferentes.")
    else:
        r = df[x].corr(df[y])
        k1, k2, k3 = st.columns(3)
        k1.metric("r de Pearson", "indefinido" if np.isnan(r) else fmt_num(r, 3))
        k2.metric("r² (variação explicada)", "—" if np.isnan(r) else f"{fmt_num(100 * r**2, 1)}%")
        k3.metric("Classificação", est.classificar_pearson(r))
        st.caption("Regra usada: |r| ≥ 0,7 forte · 0,3 ≤ |r| < 0,7 moderada · |r| < 0,3 fraca ou nula.")

    st.warning(
        "⚠️ **Correlação não implica causalidade.** Um r alto indica que as variáveis "
        "variam juntas, mas não prova que uma causa a outra (pode haver uma terceira "
        "variável envolvida, como a estação do ano)."
    )

    # ---- Matriz de correlação ----------------------------------------------------------------
    st.markdown("**Matriz de correlação geral**")
    matriz = df[cols].corr()
    modo = st.radio("Visualização", ["Mapa de calor", "Tabela"], horizontal=True, key="bi_modo")
    if modo == "Mapa de calor":
        fig = _mapa_de_calor(matriz)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.dataframe(matriz.round(3))
