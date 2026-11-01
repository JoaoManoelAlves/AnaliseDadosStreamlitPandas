"""
dados.py
========
Bloco 0 (parte de performance) e higienização da base.

Responsabilidades:
  1. Ler o CSV da UCI (função com @st.cache_data -> o arquivo só é lido e
     tratado uma vez, mesmo que o usuário mexa nos filtros várias vezes).
  2. Gerar o relatório de sanidade (nulos e duplicadas) ANTES do tratamento.
  3. Tratar nulos, duplicadas e tipos.
  4. Criar colunas legíveis (rótulos, unidades reais, nomes em português).
  5. Montar o dicionário de dados exibido na Aba 1.
"""
import pandas as pd
import streamlit as st

import config


@st.cache_data(show_spinner="Carregando e tratando a base...")
def carregar_dados(caminho_csv: str):
    """Lê, valida e trata o CSV. Retorna (df_tratado, relatorio_sanidade)."""
    bruto = pd.read_csv(caminho_csv)

    # --- Validação: a base precisa conter as colunas esperadas -------------
    faltando = [c for c in config.COLUNAS_ORIGINAIS_OBRIGATORIAS if c not in bruto.columns]
    if faltando:
        raise ValueError(f"O CSV não contém as colunas esperadas: {faltando}")

    # --- Relatório de sanidade (feito sobre os dados brutos) ---------------
    nulos_por_coluna = bruto.isna().sum()
    relatorio = {
        "linhas_originais": int(len(bruto)),
        "nulos_por_coluna": nulos_por_coluna[nulos_por_coluna > 0],
        "total_nulos": int(nulos_por_coluna.sum()),
        "duplicadas": int(bruto.duplicated().sum()),
    }

    df = bruto.copy()

    # --- Tratamento ---------------------------------------------------------
    # 1) Duplicadas: removidas.
    df = df.drop_duplicates()

    # 2) Data: converte texto -> datetime. Linhas sem data válida são descartadas
    #    porque perdem o sentido em uma série diária.
    df["dteday"] = pd.to_datetime(df["dteday"], errors="coerce")
    df = df.dropna(subset=["dteday"])

    # 3) Nulos nas demais colunas:
    #    - colunas de código (categorias numéricas) -> moda (valor mais comum)
    #    - colunas contínuas/contagens              -> mediana (robusta a outliers)
    codigos = ["season", "yr", "mnth", "holiday", "weekday", "workingday", "weathersit"]
    medidas = ["temp", "atemp", "hum", "windspeed", "casual", "registered", "cnt"]
    for col in codigos:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].mode().iloc[0])
    for col in medidas:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())

    # 4) Recalcula o total para garantir consistência (cnt = casual + registered)
    #    -- só corrige se houver divergência.
    soma = df["casual"] + df["registered"]
    df["cnt"] = df["cnt"].where(df["cnt"] == soma, soma)

    # --- Colunas derivadas e legíveis --------------------------------------
    out = pd.DataFrame()
    out["data"] = df["dteday"]
    out["estacao"] = df["season"].astype(int).map(config.MAPA_ESTACAO)
    out["ano"] = df["yr"].astype(int).map(config.MAPA_ANO)
    out["mes"] = df["mnth"].astype(int)
    out["dia_semana"] = df["dteday"].dt.dayofweek.map(config.MAPA_DIA_SEMANA)
    out["feriado"] = df["holiday"].astype(int).map({0: "Não", 1: "Sim"})
    out["tipo_dia"] = df["workingday"].astype(int).map(
        {1: "Dia útil", 0: "Fim de semana / feriado"}
    )
    out["clima"] = df["weathersit"].astype(int).map(config.MAPA_CLIMA)

    # Desnormalização para unidades reais
    out["temp_c"] = df["temp"] * (config.TEMP_MAX - config.TEMP_MIN) + config.TEMP_MIN
    out["sensacao_c"] = df["atemp"] * (config.ATEMP_MAX - config.ATEMP_MIN) + config.ATEMP_MIN
    out["umidade_pct"] = df["hum"] * config.HUM_MAX
    out["vento_kmh"] = df["windspeed"] * config.VENTO_MAX

    out["usuarios_casuais"] = df["casual"].astype(int)
    out["usuarios_registrados"] = df["registered"].astype(int)
    out["total_alugueis"] = df["cnt"].astype(int)

    out = out.reset_index(drop=True)
    relatorio["linhas_finais"] = int(len(out))
    return out, relatorio


def montar_dicionario(df: pd.DataFrame) -> pd.DataFrame:
    """Tabela descritiva das colunas (significado, unidade e tipo de dado)."""
    linhas = [
        ("data", "dteday", "Data da observação (uma linha por dia)", "AAAA-MM-DD", "Data"),
        ("estacao", "season", "Estação do ano (rótulos conforme a documentação UCI)", "—", "Categórica nominal"),
        ("ano", "yr", "Ano da observação (0 = 2011, 1 = 2012)", "—", "Categórica"),
        ("mes", "mnth", "Mês do ano", "1 a 12", "Discreta (ordinal)"),
        ("dia_semana", "weekday", "Dia da semana (derivado da data)", "—", "Categórica ordinal"),
        ("feriado", "holiday", "Indica se o dia é feriado", "Sim / Não", "Categórica binária"),
        ("tipo_dia", "workingday", "Dia útil = nem fim de semana nem feriado", "—", "Categórica binária"),
        ("clima", "weathersit", "Condição climática (1 limpo ... 4 chuva/neve forte)", "—", "Categórica ordinal"),
        ("temp_c", "temp", "Temperatura do ar (desnormalizada: temp × 47 − 8)", "°C", "Numérica contínua"),
        ("sensacao_c", "atemp", "Sensação térmica (desnormalizada: atemp × 66 − 16)", "°C", "Numérica contínua"),
        ("umidade_pct", "hum", "Umidade relativa do ar (hum × 100)", "%", "Numérica contínua"),
        ("vento_kmh", "windspeed", "Velocidade do vento (windspeed × 67; unidade assumida)", "km/h", "Numérica contínua"),
        ("usuarios_casuais", "casual", "Aluguéis feitos por usuários não cadastrados", "aluguéis/dia", "Numérica discreta"),
        ("usuarios_registrados", "registered", "Aluguéis feitos por usuários cadastrados", "aluguéis/dia", "Numérica discreta"),
        ("total_alugueis", "cnt", "Total de aluguéis no dia (casuais + registrados)", "aluguéis/dia", "Numérica discreta"),
    ]
    dic = pd.DataFrame(
        linhas,
        columns=["Coluna (no app)", "Coluna original (UCI)", "Significado", "Unidade", "Tipo de dado"],
    )
    # Tipo real inferido pelo Pandas (confere se a tipagem ficou correta)
    dic["dtype (Pandas)"] = dic["Coluna (no app)"].map(lambda c: str(df[c].dtype))
    return dic
