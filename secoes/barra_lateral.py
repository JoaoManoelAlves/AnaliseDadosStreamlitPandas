"""
secoes/barra_lateral.py  —  BLOCO 1: barra lateral de controle
==============================================================
Mostra a identificação do projeto, aplica os filtros e exibe o contador
dinâmico de linhas. Devolve o DataFrame já filtrado para o restante do app.
"""
import math

import pandas as pd
import streamlit as st

import config
from estatistica import fmt_num


def renderizar(df: pd.DataFrame) -> pd.DataFrame:
    sb = st.sidebar

    # ---- Identificação do dataset ----------------------------------------
    sb.title("🚲 Bike Sharing")
    sb.markdown(f"**Dataset:** {config.NOME_DATASET}")
    sb.markdown(f"**Fonte oficial (UCI):** [{config.LINK_UCI}]({config.LINK_UCI})")
    sb.markdown("**Autores do app:** " + " e ".join(config.AUTORES))
    sb.markdown(f"**Objetivo:** {config.OBJETIVO}")
    sb.divider()

    # ---- Filtros -----------------------------------------------------------
    sb.header("Filtros")

    # Filtros categóricos (st.multiselect). Por padrão tudo vem selecionado.
    estacoes = sb.multiselect(
        "Estação do ano",
        options=list(config.MAPA_ESTACAO.values()),
        default=list(config.MAPA_ESTACAO.values()),
        key="f_estacao",
    )
    anos = sb.multiselect(
        "Ano",
        options=list(config.MAPA_ANO.values()),
        default=list(config.MAPA_ANO.values()),
        key="f_ano",
    )
    climas_disponiveis = [c for c in config.MAPA_CLIMA.values() if c in set(df["clima"])]
    climas = sb.multiselect(
        "Condição climática",
        options=climas_disponiveis,
        default=climas_disponiveis,
        key="f_clima",
    )

    # Filtro numérico (st.slider) de faixa de temperatura
    t_min = float(math.floor(df["temp_c"].min()))
    t_max = float(math.ceil(df["temp_c"].max()))
    faixa_temp = sb.slider(
        "Temperatura (°C)",
        min_value=t_min,
        max_value=t_max,
        value=(t_min, t_max),
        step=0.5,
        key="f_temp",
    )

    # ---- Aplicação dos filtros ---------------------------------------------
    filtro = (
        df["estacao"].isin(estacoes)
        & df["ano"].isin(anos)
        & df["clima"].isin(climas)
        & df["temp_c"].between(faixa_temp[0], faixa_temp[1])
    )
    df_filtrado = df[filtro]

    # ---- Contador dinâmico ---------------------------------------------------
    total, atual = len(df), len(df_filtrado)
    pct = 100 * atual / total if total else 0
    sb.divider()
    sb.info(f"Exibindo **{atual} de {total}** registros ({fmt_num(pct, 1)}%)")

    return df_filtrado
