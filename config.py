"""
config.py
=========
Configurações e constantes centrais do dashboard.

Tudo o que é "texto fixo" ou "regra de negócio" (caminhos, autores, rótulos,
mapeamentos de códigos) fica aqui. Assim, os demais módulos não precisam
conhecer detalhes da base e o app inteiro pode ser ajustado em um único lugar.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
# Usamos o arquivo diário (day.csv): 731 linhas, uma por dia de 2011 a 2012.
CAMINHO_CSV = BASE_DIR / "database" / "day.csv"

# ---------------------------------------------------------------------------
# Identificação do projeto (exibida na barra lateral)
# ---------------------------------------------------------------------------
NOME_DATASET = "Bike Sharing Dataset"
LINK_UCI = "https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset"
AUTORES = ["João Manoel", "Kaio Javã"]
OBJETIVO = (
    "Entender como clima, estação e tipo de dia influenciam a demanda diária "
    "de aluguel de bicicletas do sistema Capital Bikeshare (Washington, D.C.), "
    "usando estatística descritiva, outliers (Tukey) e correlação de Pearson."
)

# ---------------------------------------------------------------------------
# Mapeamentos dos códigos numéricos da base para rótulos legíveis
# (conforme a documentação oficial da UCI)
# ---------------------------------------------------------------------------
MAPA_ESTACAO = {1: "Primavera", 2: "Verão", 3: "Outono", 4: "Inverno"}
MAPA_ANO = {0: "2011", 1: "2012"}
MAPA_CLIMA = {
    1: "Limpo / poucas nuvens",
    2: "Nublado / névoa",
    3: "Chuva ou neve leve",
    4: "Chuva ou neve forte",
}
MAPA_DIA_SEMANA = {
    0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta",
    4: "Sexta", 5: "Sábado", 6: "Domingo",
}  # índice vindo de datetime.dayofweek (segunda = 0)

# ---------------------------------------------------------------------------
# Fatores de desnormalização
# A UCI entrega temp, atemp, hum e windspeed já normalizados (0 a 1).
# Convertemos de volta para unidades reais para facilitar a leitura.
#   temp   = (t - t_min) / (t_max - t_min), t_min = -8,  t_max = 39  -> °C
#   atemp  = (t - t_min) / (t_max - t_min), t_min = -16, t_max = 50  -> °C
#   hum    = umidade / 100                                           -> %
#   windspeed = vento / 67                                           -> km/h
# ---------------------------------------------------------------------------
TEMP_MIN, TEMP_MAX = -8, 39
ATEMP_MIN, ATEMP_MAX = -16, 50
HUM_MAX = 100
VENTO_MAX = 67

# ---------------------------------------------------------------------------
# Colunas usadas pelo dashboard (nomes já em português, após o tratamento)
# ---------------------------------------------------------------------------
COLUNAS_NUMERICAS = [
    "temp_c",
    "sensacao_c",
    "umidade_pct",
    "vento_kmh",
    "usuarios_casuais",
    "usuarios_registrados",
    "total_alugueis",
]
COLUNAS_CATEGORICAS = ["estacao", "ano", "clima", "dia_semana", "tipo_dia", "feriado"]

# Rótulos amigáveis para menus, gráficos e tabelas
ROTULOS = {
    "temp_c": "Temperatura (°C)",
    "sensacao_c": "Sensação térmica (°C)",
    "umidade_pct": "Umidade relativa (%)",
    "vento_kmh": "Velocidade do vento (km/h)",
    "usuarios_casuais": "Usuários casuais (aluguéis/dia)",
    "usuarios_registrados": "Usuários registrados (aluguéis/dia)",
    "total_alugueis": "Total de aluguéis (por dia)",
    "estacao": "Estação do ano",
    "ano": "Ano",
    "clima": "Condição climática",
    "dia_semana": "Dia da semana",
    "tipo_dia": "Tipo de dia",
    "feriado": "Feriado",
}

# Colunas originais que a base da UCI precisa ter (validação na leitura)
COLUNAS_ORIGINAIS_OBRIGATORIAS = [
    "dteday", "season", "yr", "mnth", "holiday", "weekday", "workingday",
    "weathersit", "temp", "atemp", "hum", "windspeed",
    "casual", "registered", "cnt",
]
