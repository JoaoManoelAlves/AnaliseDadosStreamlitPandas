"""
secoes/aba_parecer.py  —  ABA 4: parecer analítico e conclusões
===============================================================
Parte 1: tabelas dinâmicas (respondem aos filtros) que servem de evidência.
Parte 2: texto da equipe respondendo às 4 perguntas norteadoras.
"""
import pandas as pd
import streamlit as st

import config
import estatistica as est


def _tabela_evidencias(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for col in config.COLUNAS_NUMERICAS:
        s = df[col].dropna()
        r = est.resumo_univariado(s)
        tk = est.limites_tukey(s)
        rotulo, _, _ = est.diagnostico_assimetria(r["media"], r["mediana"], r["desvio"])
        linhas.append({
            "Variável": config.ROTULOS[col],
            "Média": round(r["media"], 2),
            "Mediana": round(r["mediana"], 2),
            "Assimetria": round(r["assimetria"], 2),
            "Outliers (%)": round(tk["percentual"], 1),
            "Diagnóstico": rotulo.split(" (")[0],
        })
    return pd.DataFrame(linhas)


def renderizar(df: pd.DataFrame):
    st.subheader("📝 Parecer analítico e conclusões")

    if len(df) < 10:
        st.warning("Poucos registros após os filtros para gerar as evidências.")
        return

    # ---- Evidências dinâmicas --------------------------------------------------------------
    st.markdown("#### Evidências (recalculadas conforme os filtros)")
    st.dataframe(_tabela_evidencias(df), hide_index=True)
    st.markdown("**Pares de variáveis mais correlacionados**")
    top = est.pares_mais_correlacionados(df[config.COLUNAS_NUMERICAS].corr(), n=5)
    top["Variável A"] = top["Variável A"].map(config.ROTULOS)
    top["Variável B"] = top["Variável B"].map(config.ROTULOS)
    top["r"] = top["r"].round(3)
    st.dataframe(top, hide_index=True)

    st.caption(
        "O texto abaixo interpreta a base completa (2011–2012, sem filtros). "
        "Use as tabelas acima para conferir como os números mudam ao filtrar."
    )

    # ---- Texto da equipe ----------------------------------------------------------------------
    st.markdown("#### Respostas às perguntas norteadoras")
    autores = " e ".join(config.AUTORES)
    st.markdown(
        f"""
**Equipe:** {autores}

**(a) Quais variáveis exibem forte assimetria e qual a razão prática?**

A variável **usuários casuais** é a mais assimétrica: a média fica bem acima da mediana
(cauda à direita), porque há muitos dias de uso baixo e poucos dias de pico, em geral
fins de semana e feriados com bom tempo. A **velocidade do vento** também tem cauda à
direita, mais leve. Já **total de aluguéis** e **temperatura** ficam bem próximas da
simetria. Na prática, para os casuais a **mediana** descreve melhor o "dia típico";
usar a média levaria a superestimar a demanda rotineira e a dimensionar a frota para
um cenário que só acontece em dias especiais.

**(b) Os outliers detectados decorrem de erros ou refletem comportamentos legítimos?**

A maior parte reflete **comportamento legítimo do domínio**: picos de usuários casuais
em dias de clima favorável e rajadas de vento fortes são fenômenos reais, não falhas
de registro. Já os **valores muito baixos de demanda** costumam coincidir com eventos
climáticos extremos (por exemplo, o dia de menor uso da base aparece no fim de outubro
de 2012, período da passagem do furacão Sandy), o que também é legítimo. Valores de
umidade próximos de zero, se aparecerem na Aba 2, são fisicamente improváveis e devem
ser **validados** como possível erro de medição.

**(c) Quais pares exibem correlação relevante e qual o impacto prático dessa relação?**

- **Temperatura × sensação térmica:** correlação muito forte (quase 1). São praticamente
  a mesma informação, então, em um modelo, basta usar uma delas (evita redundância).
- **Total × usuários registrados:** correlação muito forte, em parte *por construção*,
  pois o total é a soma de casuais e registrados e os registrados são a maioria.
- **Temperatura × total de aluguéis:** correlação positiva moderada. Dias mais quentes
  tendem a ter mais aluguéis, tornando a temperatura o principal fator climático da demanda.
- **Vento × total de aluguéis:** correlação negativa fraca; **umidade** tem relação fraca.

Atenção: correlação não implica causalidade. A estação do ano e o crescimento do sistema
de 2011 para 2012 também influenciam a demanda e podem inflar essas relações.

**(d) Que decisão um gestor poderia tomar a partir dos dados filtrados?**

- Concentrar a **manutenção preventiva** da frota nos meses de menor demanda (estações
  frias e dias de clima ruim), liberando bicicletas para os meses de pico.
- **Reforçar a oferta** de bicicletas e docas em dias quentes e de tempo limpo, usando a
  previsão do tempo como gatilho operacional.
- Criar **campanhas para usuários casuais** em fins de semana e feriados com bom tempo,
  convertendo-os em registrados, que representam a base estável de demanda.
- Usar o filtro de **ano** para comparar 2011 e 2012 e medir o crescimento do sistema.
"""
    )
