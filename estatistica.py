"""
estatistica.py
==============
Funções puras (sem Streamlit) com os cálculos estatísticos do trabalho.
Separar o "cálculo" da "tela" facilita testar e reaproveitar o código.
"""
import numpy as np
import pandas as pd


def fmt_num(valor: float, casas: int = 2) -> str:
    """Formata número no padrão brasileiro: 1.234,56"""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def resumo_univariado(serie: pd.Series) -> dict:
    """Média, mediana, desvio padrão, quartis, IQR e assimetria."""
    q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
    return {
        "media": serie.mean(),
        "mediana": serie.median(),
        "desvio": serie.std(),          # desvio padrão amostral (ddof=1)
        "q1": q1,
        "q3": q3,
        "iqr": q3 - q1,                 # Intervalo Interquartil
        "assimetria": serie.skew(),     # coeficiente de assimetria
    }


def limites_tukey(serie: pd.Series) -> dict:
    """
    Critério empírico de Tukey:
        Limite inferior = Q1 - 1,5 × IQR
        Limite superior = Q3 + 1,5 × IQR
    Valores fora desse intervalo são "potenciais outliers".
    """
    r = resumo_univariado(serie)
    inf = r["q1"] - 1.5 * r["iqr"]
    sup = r["q3"] + 1.5 * r["iqr"]
    mascara = (serie < inf) | (serie > sup)
    return {
        "inferior": inf,
        "superior": sup,
        "mascara": mascara,
        "total": int(mascara.sum()),
        "percentual": 100 * mascara.sum() / len(serie) if len(serie) else 0.0,
    }


def diagnostico_assimetria(media: float, mediana: float, desvio: float):
    """
    Compara média e mediana e devolve (rótulo, explicação, métrica recomendada).
    Tolerância: diferença menor que 10% do desvio padrão é tratada como
    "aproximadamente iguais".
    """
    if desvio == 0 or np.isnan(desvio) or abs(media - mediana) <= 0.1 * desvio:
        return (
            "Média ≈ Mediana (distribuição aproximadamente simétrica)",
            "Os valores se distribuem de forma equilibrada em torno do centro, "
            "sem caudas dominantes.",
            "Média (junto com o desvio padrão), pois resume bem o centro.",
        )
    if media > mediana:
        return (
            "Média > Mediana (assimetria positiva / cauda à direita)",
            "Poucos valores muito altos puxam a média para cima, enquanto a "
            "maioria dos dias fica abaixo dela.",
            "Mediana (junto com o IQR), pois não é distorcida pelos valores extremos.",
        )
    return (
        "Média < Mediana (assimetria negativa / cauda à esquerda)",
        "Poucos valores muito baixos puxam a média para baixo, enquanto a "
        "maioria dos dias fica acima dela.",
        "Mediana (junto com o IQR), pois não é distorcida pelos valores extremos.",
    )


def classificar_pearson(r: float) -> str:
    """Classificação qualitativa de |r| (convenção usual em sala de aula)."""
    if np.isnan(r):
        return "indefinida"
    forca = abs(r)
    if forca >= 0.7:
        nivel = "forte"
    elif forca >= 0.3:
        nivel = "moderada"
    else:
        nivel = "fraca ou nula"
    if nivel == "fraca ou nula":
        return nivel
    sentido = "positiva" if r > 0 else "negativa"
    return f"{nivel} {sentido}"


def pares_mais_correlacionados(matriz: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Lista os n pares de variáveis com maior |r| (sem repetir pares)."""
    pares = []
    cols = list(matriz.columns)
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            pares.append((a, b, matriz.loc[a, b]))
    tabela = pd.DataFrame(pares, columns=["Variável A", "Variável B", "r"])
    tabela["|r|"] = tabela["r"].abs()
    return tabela.sort_values("|r|", ascending=False).head(n).drop(columns="|r|")
