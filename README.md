# 🚲 Dashboard de Estatística Descritiva — Bike Sharing (UCI)

Dashboard interativo em **Streamlit** que explora a demanda diária de aluguel de bicicletas
do sistema *Capital Bikeshare* (Washington, D.C.), usando estatística descritiva, detecção de
outliers pelo critério de Tukey e correlação linear de Pearson.

| | |
|---|---|
| **Autores** | João Manoel e Kaio Javã |
| **Instituição** | IFMA · Curso Superior de TSI |
| **Disciplina** | Tópicos Especiais em Programação / Análise de Dados |
| **Professor** | Prof. Breno Caetano |
| **Dataset** | [Bike Sharing Dataset — UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset) |

---

## 📌 Sobre o projeto

**Objetivo da análise:** entender como clima, estação do ano e tipo de dia influenciam o
número de bicicletas alugadas por dia e que decisões um gestor do sistema poderia tomar a
partir disso.

**Sobre a base:** usamos o arquivo `day.csv`, com **731 linhas** (um dia de 2011 a 2012 por
linha), **7 variáveis numéricas** e **6 categóricas**.

## ✨ Funcionalidades

- **Barra lateral:** identificação do dataset, filtros por estação, ano, condição climática e faixa
  de temperatura, e contador dinâmico ("Exibindo X de Y registros (Z%)").
- **Aba 1 — Dicionário e amostragem:** significado, unidade e tipo de cada coluna; relatório de
  sanidade (nulos e duplicadas); amostra da base com slider de quantidade de linhas.
- **Aba 2 — Univariada e outliers:** média, mediana, desvio padrão e IQR em cartões; `describe()`;
  diagnóstico de assimetria; histograma com bins ajustáveis; boxplot; limites de Tukey com total e
  percentual de outliers.
- **Aba 3 — Bivariada e correlação:** dispersão com eixos configuráveis, cor por categoria e reta
  de tendência; r de Pearson classificado; alerta de que correlação não implica causalidade;
  matriz de correlação em mapa de calor ou tabela.
- **Aba 4 — Parecer analítico:** tabelas de evidência que respondem aos filtros e respostas às
  quatro perguntas norteadoras.

## 🛠️ Tecnologias

Python 3.10+ · Streamlit · Pandas · NumPy · Matplotlib

## ▶️ Como executar

**1. Clone ou extraia o projeto** e entre na pasta:

```bash
cd dashboard-bike-sharing
```

**2. Crie um ambiente virtual:**

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows
```

**3. Instale as dependências:**

```bash
pip install -r requirements.txt
```

**4. Confira a base de dados.** O arquivo deve estar em `database/day.csv`. Se não estiver:
baixe o .zip na [página da UCI](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset),
extraia e copie o `day.csv` para a pasta `database/`.

**5. Inicie o app:**

```bash
streamlit run app.py
```

O navegador abre em `http://localhost:8501`.

## 🗂️ Estrutura do projeto

```
dashboard-bike-sharing/
├── app.py                    # Ponto de entrada: configura a página, carrega dados e monta as abas
├── config.py                 # Constantes: caminho do CSV, autores, rótulos e mapeamentos
├── dados.py                  # Leitura com @st.cache_data, higienização e dicionário de dados
├── estatistica.py            # Cálculos puros: média, IQR, Tukey, assimetria, Pearson
├── secoes/
│   ├── barra_lateral.py      # Bloco 1: identificação, filtros e contador
│   ├── aba_dicionario.py     # Aba 1
│   ├── aba_univariada.py     # Aba 2
│   ├── aba_bivariada.py      # Aba 3
│   └── aba_parecer.py        # Aba 4
├── database/
│   └── day.csv               # Base de dados da UCI
├── requirements.txt
└── README.md
```

**Por que modularizar?** O `app.py` fica curto; cada aba pode ser editada sem afetar as outras;
e os cálculos ficam separados da interface, o que facilita testar e reaproveitar o código.

## 🔄 Fluxo da aplicação

```
database/day.csv ──► dados.carregar_dados() ──► DataFrame tratado (com cache)
                                                      │
                          secoes/barra_lateral.py ◄───┘  aplica filtros
                                      │
                                      ▼  DataFrame filtrado
        ┌───────────────┬──────────────┬───────────────┬───────────────┐
        │ Aba 1         │ Aba 2        │ Aba 3         │ Aba 4         │
        │ Dicionário    │ Univariada   │ Bivariada     │ Parecer       │
        └───────────────┴──────────────┴───────────────┴───────────────┘
                      todas usam estatistica.py para os cálculos
```

## 🧹 Tratamento dos dados

| Etapa | O que é feito |
|---|---|
| Duplicadas | Removidas com `drop_duplicates()` |
| Datas | Convertidas para `datetime`; linhas com data inválida são descartadas |
| Nulos em códigos categóricos | Preenchidos com a **moda** |
| Nulos em medidas numéricas | Preenchidos com a **mediana** (robusta a outliers) |
| Consistência | `total_alugueis` é conferido contra `casuais + registrados` |
| Normalização | `temp`, `atemp`, `hum` e `windspeed` voltam para °C, °C, % e km/h |
| Rótulos | Colunas renomeadas para português; códigos de estação, ano e clima viram texto |

A base da UCI costuma chegar sem nulos nem duplicadas; o código está preparado para o caso
de aparecerem, e a Aba 1 mostra as contagens.

> **Nota sobre o vento:** a UCI não especifica a unidade de `windspeed`; assumimos km/h
> (valor normalizado × 67).

## 📐 Critérios estatísticos adotados

- **Assimetria:** compara média e mediana. Diferença menor que 10% do desvio padrão é tratada
  como "Média ≈ Mediana". Caso contrário, indica cauda à direita (média > mediana) ou à
  esquerda (média < mediana) e recomenda a mediana como medida central.
- **Outliers (Tukey):** `LI = Q1 − 1,5 × IQR` e `LS = Q3 + 1,5 × IQR`. Valores fora do
  intervalo são *potenciais* outliers, não necessariamente erros.
- **Correlação de Pearson:** |r| ≥ 0,7 forte · 0,3 ≤ |r| < 0,7 moderada · |r| < 0,3 fraca ou nula.

## 🧾 Dicionário resumido das variáveis

| Variável (no app) | Original (UCI) | Descrição | Unidade |
|---|---|---|---|
| `data` | dteday | Data da observação | AAAA-MM-DD |
| `estacao` | season | Estação do ano | — |
| `ano` | yr | 2011 ou 2012 | — |
| `mes` | mnth | Mês | 1 a 12 |
| `dia_semana` | weekday | Dia da semana | — |
| `feriado` | holiday | Dia é feriado? | Sim/Não |
| `tipo_dia` | workingday | Dia útil ou fim de semana/feriado | — |
| `clima` | weathersit | Condição climática (1 limpo a 4 chuva/neve forte) | — |
| `temp_c` | temp | Temperatura | °C |
| `sensacao_c` | atemp | Sensação térmica | °C |
| `umidade_pct` | hum | Umidade relativa | % |
| `vento_kmh` | windspeed | Velocidade do vento | km/h |
| `usuarios_casuais` | casual | Aluguéis de usuários não cadastrados | aluguéis/dia |
| `usuarios_registrados` | registered | Aluguéis de usuários cadastrados | aluguéis/dia |
| `total_alugueis` | cnt | Total de aluguéis no dia | aluguéis/dia |

A tabela completa (com tipo de dado) está na Aba 1 do app.

## ❓ Problemas comuns

- **"Arquivo day.csv não encontrado":** copie o `day.csv` para `database/`.
- **`ModuleNotFoundError`:** rode `pip install -r requirements.txt` no ambiente que está usando.
- **Tela vazia ou aviso de filtros:** os filtros da barra lateral não retornaram nenhum registro;
  amplie a seleção.

## 📚 Referências

- GRUS, Joel. *Data Science do Zero: Primeiras Regras com o Python*. Rio de Janeiro: Alta Books.
- McKINNEY, Wes. *Python para Análise de Dados*. São Paulo: Novatec.
- FANAEE-T, Hadi. *Bike Sharing* [Dataset]. UCI Machine Learning Repository, 2013.
  https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset

---

Desenvolvido por **João Manoel** e **Kaio Javã** — IFMA · TSI.