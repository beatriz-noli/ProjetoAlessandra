import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ======================================================
# Carregar dados
# ======================================================

# Exemplos
exames = pd.read_csv("exames.csv")
url_pacientes = "https://docs.google.com/spreadsheets/d/134QN9guFzVBUIctT9R1l0d7uZzVEYoyY/export?format=xlsx"
xls_pacientes = pd.ExcelFile(url_pacientes)
pacientes = pd.read_excel(xls_pacientes, sheet_name="Tabela", header=0)

exames.columns = exames.columns.str.strip()
pacientes.columns = pacientes.columns.str.strip()

# Junta os dois DataFrames
df = exames.merge(
    pacientes[["PACIENTE", "DESFECHO"]],
    left_on="Paciente",
    right_on="PACIENTE",
    how="left"
)
df = df.drop(columns="PACIENTE")

# Remove linhas sem desfecho
df = df.dropna(subset=["Exame-Parametro", "DESFECHO", "Valor"])
df = df[df["Data"]<=20]

df = (
    df
    .groupby(["Paciente", "DESFECHO", "Exame-Parametro", "Data"])["Valor"]
    .mean()
    .reset_index()
)

# ======================================================
# Sidebar
# ======================================================

st.sidebar.title("Filtros")

tipo_grafico = st.sidebar.radio(
    "Tipo de gráfico",
    ["Linha", "Boxplot"]
)

exame = st.sidebar.selectbox(
    "Selecione o exame",
    sorted(df["Exame-Parametro"].unique())
)

mostrar_individuos = st.sidebar.checkbox(
    "Mostrar pacientes",
    value=True
)

grupos = st.sidebar.multiselect(
    "Grupos",
    options=["ALTA", "OBITO"],
    default=["ALTA", "OBITO"]
)

# ======================================================
# Filtrar exame
# ======================================================

dados = df[
    (df["Exame-Parametro"] == exame) &
    (df["DESFECHO"].isin(grupos))
].copy()

# ======================================================
# Média por grupo
# ======================================================

estatisticas = (
    dados
    .groupby(["DESFECHO", "Data"])["Valor"]
    .agg(
        media="mean",
        n="count"
    )
    .reset_index()
)

# ======================================================
# Gráfico
# ======================================================

cores = {
    "ALTA": "#1f77b4",
    "OBITO": "#d62728"
}

fig = go.Figure()

# ----------------------------
# Linhas individuais
# ----------------------------
if tipo_grafico == "Linha":

    # ----------------------------
    # Linhas individuais
    # ----------------------------

    if mostrar_individuos:

        for grupo in grupos:

            pacientes_grupo = (
                dados[dados["DESFECHO"] == grupo]["Paciente"]
                .unique()
            )

            for paciente in pacientes_grupo:

                temp = dados[
                    (dados["DESFECHO"] == grupo) &
                    (dados["Paciente"] == paciente)
                ].sort_values("Data")

                fig.add_trace(
                    go.Scatter(
                        x=temp["Data"],
                        y=temp["Valor"],
                        mode="lines",
                        line=dict(
                            color=cores[grupo],
                            width=1
                        ),
                        opacity=0.5,
                        showlegend=False,
                        hoverinfo="skip"
                    )
                )

    # Médias

    for grupo in grupos:

        temp = estatisticas[estatisticas["DESFECHO"] == grupo]

        fig.add_trace(
            go.Scatter(
                x=temp["Data"],
                y=temp["media"],
                mode="lines+markers",
                name=f"Média {grupo}",
                line=dict(
                    color=cores[grupo],
                    width=4
                ),
                marker=dict(size=7),
                customdata=temp["n"],
                hovertemplate=(
                    "<b>Grupo:</b> " + grupo +
                    "<br><b>Dia:</b> %{x}" +
                    "<br><b>Média:</b> %{y:.2f}" +
                    "<br><b>Pacientes:</b> %{customdata}" +
                    "<extra></extra>"
                )
            )
        )

else:

    for grupo in grupos:

        temp = dados[dados["DESFECHO"] == grupo]

        fig.add_trace(
            go.Box(
                x=temp["Data"].astype(str),
                y=temp["Valor"],
                name=grupo,
                marker_color=cores[grupo],
                boxmean=True,      # mostra a média
                boxpoints="outliers",  # ou "all"
                offsetgroup=grupo 
            )
        )

# ======================================================
# Layout
# ======================================================

fig.update_layout(
    title=f"{exame}",
    xaxis_title="Dia Relativo",
    yaxis_title=exame,
    template="plotly_white",
    legend_title="Grupo",
    boxmode="group",
    height=700
)

st.title("Dashboard dos Exames")

st.plotly_chart(
    fig,
    width="stretch"
)