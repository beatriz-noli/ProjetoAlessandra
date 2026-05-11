import pandas as pd
import matplotlib.pyplot as plt

#%% URLs dos dados
url_hemogramas = "https://docs.google.com/spreadsheets/d/19dfvCBynglk-YGBYjxN_M_I3QAusQEMfuTsarrGiAPw/export?format=xlsx"
url_sinais = "https://docs.google.com/spreadsheets/d/1MwdppHk_WDdVFSAG3ZzkXoE9MHLSfGMKbOaziZruyEw/export?format=xlsx"


#%% Leitura dos arquivos Excel
xls_hemogramas = pd.ExcelFile(url_hemogramas)
xls_sinais = pd.ExcelFile(url_sinais)


#%% Filtrar abas relevantes
abas_filtradas_hemograma = [s for s in xls_hemogramas.sheet_names if s.startswith("p")]
abas_filtradas_sinais = [s for s in xls_sinais.sheet_names if s.startswith("p")]


#%% Concatenar abas
Tabela_hemogramas = pd.concat(
    (
        pd.read_excel(xls_hemogramas, sheet_name=aba, header=0)
        for aba in abas_filtradas_hemograma
    ),
    ignore_index=True
)

Tabela_hemogramas.columns = Tabela_hemogramas.columns.str.upper()

Tabela_sinais = pd.concat(
    (
        pd.read_excel(xls_sinais, sheet_name=aba, header=0)
        for aba in abas_filtradas_sinais
    ),
    ignore_index=True
)

Tabela_sinais.columns = Tabela_sinais.columns.str.upper()
Tabela_sinais.rename(columns={'PARÂMETRO': 'PARAMETRO', 'VALOR': 'VALOR NUMÉRICO'}, inplace=True)


#%% Limpeza inicial
Tabela_hemogramas.dropna(how="all", inplace=True)
Tabela_sinais.dropna(how="all", inplace=True)

Tabela_hemogramas["EXAME"] = Tabela_hemogramas["EXAME"].str.strip()
Tabela_hemogramas["PARAMETRO"] = Tabela_hemogramas["PARAMETRO"].str.strip()

Tabela_sinais["EXAME"] = Tabela_sinais["EXAME"].str.strip()
Tabela_sinais["PARAMETRO"] = Tabela_sinais["PARAMETRO"].str.strip()

#%% arrumar itens
substituicoes_exame = {
    "LP-SÓDIO - NA": "LP-SÓDIO-NA",
    "LP-POTÁSSIO - K": "LP-POTÁSSIO-K",
    "LP-PÓTASSIO-K": "LP-POTÁSSIO-K",
    "LP-POTASSIO-K": "LP-POTÁSSIO-K",
    "LP-CLORO - CLORETO": "LP-CLORO-CLORETO",
    "LP-ÁCIDO LÁCTICO - LACTATO": "LP-ÁCIDO LÁCTICO-LACTATO",
    "LP-CULTURA DE BACTERIA-ASPIRADO TRAQUEAL 1 AMOSTRA": 'LP-CULTURA DE BACTÉRIA - ASPIRADO TRAQUEAL 1ª AMOSTRA',
    "LP-ALANINA AMINOTRANSFERASE - (ALT/TGP)": "LP-ALANINA AMINOTRANSFERASE-(ALT/TGP)",
    "LP-CREATINOFOSFOQUINASE - CPK - CK": "LP-CREATINOFOSFOQUINASE-CPK-CK",
    "LP-TAP - TEMPO DE ATIVIDADE DE PROTROMBINA": "LP-TAP -TEMPO DE ATIVIDADE DE PROTROMBINA",
    "LP-TESTE RÁPIDO - SÍFILIS - TREPONEMA PALLIDUM": "LP-TESTE RÁPIDO - SÍFILIS-TREPONEMA PALLIDUM",
    "LP-ASPARTATO AMINOTRANSFERASE - (AST/TGO) - (AST/TGO)": "LP-ASPARTATO AMINOTRANSFERASE - (AST/TGO)-(AST/TGO)",
    "LP-TTPA - TEMPO DE TROMBOPLASTINA PARCIAL ATIVADO": "LP-TTPA-TEMPO DE TROMBOPLASTINA PARCIAL ATIVADO"
}

substituicoes_parametro = {
    "LP-CLORO - CLORETO": "LP-CLORO-CLORETO",
    "Microorganismo Isolado": "Microorganismos Isolados",
    "Microorganismo Isolado:": "Microorganismos Isolados",
    "Microorganismo isolado": "Microorganismos Isolados",
    "Microorganismo isolado:": "Microorganismos Isolados",
    "Microorganismos Isolados:": "Microorganismos Isolados",
    "Proteinas Totais": "Proteínas Totais",
    "Proteinas Totais  ": "Proteínas Totais",
    "Tempo de positividade:": "Tempo de positividade",
    "Base excess(BE)": "Base Excess(BE)",
    "CO2 Total": "CO2 TOTAL",
    "Relacao A/G": "Relação A/G",
    "Τ": "T",
    "Ρ": "P",
    "Α": "A",
    "Ο": "O"
}

for antigo, novo in substituicoes_exame.items():
    Tabela_hemogramas["EXAME"] = (
        Tabela_hemogramas["EXAME"]
        .str.replace(antigo, novo, regex=False)
    )

for antigo, novo in substituicoes_parametro.items():
    Tabela_hemogramas["PARAMETRO"] = (
        Tabela_hemogramas["PARAMETRO"]
        .str.replace(antigo, novo, regex=False)
    )
    
for valor in sorted(Tabela_hemogramas["EXAME"].dropna().unique()):
    print(repr(valor))
#%% Processamento Hemogramas

# for col in Tabela_hemogramas.columns:
#         if Tabela_hemogramas[col].dtype == "object" or pd.api.types.is_string_dtype(Tabela_hemogramas[col]):
#             Tabela_hemogramas[col] = Tabela_hemogramas[col].str.strip()

# Criar datetime
Tabela_hemogramas["DATETIME"] = pd.to_datetime(
    Tabela_hemogramas["DATA"].astype(str) + " " + Tabela_hemogramas["HORA"].astype(str),
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce"
)

Tabela_hemogramas["VALOR NUMÉRICO"] = pd.to_numeric( Tabela_hemogramas["VALOR NUMÉRICO"], errors="coerce" )

Tabela_hemogramas.drop(columns=["DATA", "HORA"], inplace=True)

# Otimizar dtypes
Tabela_hemogramas = Tabela_hemogramas.convert_dtypes()

# Dia relativo por paciente

Tabela_hemogramas["DIARELATIVO"] = (
    Tabela_hemogramas["DATETIME"] -
    Tabela_hemogramas.groupby("PACIENTE")["DATETIME"].transform("min")
).dt.days + 1

#%% Processamento Sinais Vitais
Tabela_sinais.replace("-", pd.NA, inplace=True)

# Criar datetime
Tabela_sinais["DATETIME"] = pd.to_datetime(
    Tabela_sinais["DATA"].astype(str) + " " + Tabela_sinais["HORA"].astype(str),
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce"
)

Tabela_sinais.drop(columns=["DATA", "HORA"], inplace=True)

Tabela_sinais["VALOR NUMÉRICO"] = pd.to_numeric( Tabela_sinais["VALOR NUMÉRICO"], errors="coerce" )

# Otimizar dtypes
Tabela_sinais = Tabela_sinais.convert_dtypes()

# Dia relativo por paciente

Tabela_sinais["DIARELATIVO"] = (
    Tabela_sinais["DATETIME"] -
    Tabela_sinais.groupby("PACIENTE")["DATETIME"].transform("min")
).dt.days + 1


Tabela_hemogramas_pivot_NUMERICO = Tabela_hemogramas.pivot_table(
    index=['PACIENTE', 'DIARELATIVO'],
    columns=['EXAME', 'PARAMETRO'],
    values='VALOR NUMÉRICO',
    aggfunc='mean'
)

# Tabela_hemogramas_pivot_CATEGORICO = Tabela_hemogramas.pivot_table(
#     index=['PACIENTE', 'DIARELATIVO'],
#     columns=['EXAME', 'PARAMETRO'],
#     values='VALOR CATEGÓRICO',
#     aggfunc='first'
# )

# Tabela_sinais_pivot_NUMERICO = Tabela_sinais.pivot_table(
#     index=['Paciente', 'DiaRelativo'],
#     columns=['Parâmetro'],
#     values='Valor',
#     aggfunc='first'
# )

#%% Funcoes tabela

def tab_paciente_numerico(Tabela_hemogramas, Tabela_sinais, paciente_nome):
    Tabela_hemogramas_filtrado = Tabela_hemogramas[Tabela_hemogramas['PACIENTE'] == paciente_nome]
    
    tabela1 = Tabela_hemogramas_filtrado.pivot_table(
        index='PARAMETRO',        # linhas
        columns='DATETIME',    # colunas
        values='VALOR NUMÉRICO',        # valores
        aggfunc = "mean"
    )
    
    Tabela_sinais_filtrado = Tabela_sinais[Tabela_sinais['PACIENTE'] == paciente_nome]
    
    tabela2 = Tabela_sinais_filtrado.pivot_table(
        index='PARAMETRO',        # linhas
        columns='DATETIME',    # colunas
        values='VALOR NUMÉRICO',        # valores
        aggfunc = "mean"
    )
    
    tabela = pd.concat([tabela1, tabela2])
    return tabela

def tab_exame_numerico(Tabela_hemogramas, Tabela_sinais, exame_nome):
    Tabela_hemogramas_filtrado = Tabela_hemogramas[Tabela_hemogramas['EXAME'] + " " +
                                                   Tabela_hemogramas['PARAMETRO']== exame_nome]
    
    tabela1 = Tabela_hemogramas_filtrado.pivot_table(
        index='PACIENTE',        # linhas
        columns='DIARELATIVO',    # colunas
        values='VALOR NUMÉRICO',        # valores
        aggfunc = "mean"
    )
    
    Tabela_sinais_filtrado = Tabela_sinais[Tabela_sinais['PARAMETRO'] == exame_nome]
    
    tabela2 = Tabela_sinais_filtrado.pivot_table(
        index='PACIENTE',        # linhas
        columns='DIARELATIVO',    # colunas
        values='VALOR NUMÉRICO',        # valores
        aggfunc = "mean"
    )
    
    tabela = pd.concat([tabela1, tabela2])
    return tabela

A = tab_exame_numerico(Tabela_hemogramas, Tabela_sinais, "LP-HEMOGRAMA COMPLETOBasófilos")

import re
import numpy as np
from matplotlib.lines import Line2D

def gerar_graficos(df, pasta_saida="ProjetoAlessandra/GRAFICOS"):

    df_plot = df.copy()

    # 🔥 LIMPEZA FUNDAMENTAL
    df_plot['VALOR NUMÉRICO'] = df_plot['VALOR NUMÉRICO'].astype(float)
    df_plot['DIARELATIVO'] = pd.to_numeric(df_plot['DIARELATIVO'], errors='coerce')

    # 🔹 Criar coluna combinada
    df_plot['EXAME_PARAM'] = df_plot['EXAME'] + " - " + df_plot['PARAMETRO']

    # 🔁 Loop
    for nome, grupo in df_plot.groupby('EXAME_PARAM'):

        # 🔹 remover valores inválidos
        grupo = grupo.dropna(subset=['VALOR NUMÉRICO', 'DIARELATIVO'])

        if grupo.empty:
            continue

        # 🔹 média por paciente no dia
        por_paciente = grupo.groupby(
            ['DIARELATIVO', 'PACIENTE']
        )['VALOR NUMÉRICO'].mean().reset_index()

        # 🔹 média entre pacientes
        agrupado = por_paciente.groupby('DIARELATIVO').agg(
            media=('VALOR NUMÉRICO', 'mean'),
            std=('VALOR NUMÉRICO', 'std'),
            n=('PACIENTE', 'nunique')
        ).reset_index()

        # 🔹 garantir tipos corretos
        agrupado['media'] = agrupado['media'].astype(float)
        agrupado['std'] = agrupado['std'].astype(float).fillna(0)

        if agrupado['n'].sum() == 0:
            continue

        agrupado = agrupado.sort_values('DIARELATIVO')

        plt.figure(figsize=(18, 9))

        dias = sorted(por_paciente['DIARELATIVO'].unique())
        
        dados_plot = [
            por_paciente.loc[
                por_paciente['DIARELATIVO'] == dia,
                'VALOR NUMÉRICO'
            ].dropna().values
            for dia in dias
        ]
        
        # 🔹 boxplot
        plt.boxplot(
            dados_plot,
            tick_labels=dias,
            showfliers=True,
            showmeans=True,
            meanline=True,
            medianprops=dict(color='red'),
            meanprops=dict(color='blue')
        )
        
        plt.legend(handles=[
            Line2D([0], [0], color='red', lw=2, label='Mediana'),
            Line2D([0], [0], color='blue', lw=2,  linestyle='--', label='Média')
        ])
        
        # 🔹 anotações
        for i, valores in enumerate(dados_plot):
        
            media = np.mean(valores)
            std = np.std(valores)
            n = grupo.loc[
                grupo['DIARELATIVO'] == dias[i],
                'PACIENTE'
            ].nunique()
            
            if len(valores) == 0:
                continue
            ymax = np.max(valores)
        
            plt.text(
                i + 1,
                ymax * 1.02,
                f"{media:.2f}±{std:.2f}\n(n={n})",
                ha='center',
                va='bottom',
                fontsize=8
            )
        
        plt.xlabel('Dia Relativo')
        plt.ylabel('Valor')
        plt.title(nome)
        
        plt.grid()
        plt.tight_layout()

        # 🔹 nome seguro
        nome_arquivo = re.sub(r'[\\/*?:"<>|]', "", nome)
        nome_arquivo = nome_arquivo.replace(" ", "_") + ".png"

        caminho = f"{pasta_saida}/{nome_arquivo}"

        # 🔹 salvar
        plt.savefig(caminho, dpi=300)
        plt.close()

        print(f"{nome} salvo")

    print(f"Gráficos salvos em: {pasta_saida}")