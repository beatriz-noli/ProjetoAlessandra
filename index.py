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
    Tabela_hemogramas_filtrado = Tabela_hemogramas[Tabela_hemogramas['EXAME'] + 
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

A = tab_paciente_numerico(Tabela_hemogramas, Tabela_sinais, "RN004")

import re
def gerar_graficos(df, pasta_saida="GRAFICOS"):

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

        x_pos = range(len(agrupado))

        plt.figure(figsize=(18, 9))

        plt.errorbar(
            x_pos,
            agrupado['media'],
            yerr=agrupado['std'],
            fmt='-o',
            capsize=5
        )

        plt.xticks(
            x_pos,
            agrupado['DIARELATIVO'].astype(int),
            rotation=0
        )

        # 🔹 anotações
        for i, row in agrupado.iterrows():
            if pd.notna(row['media']):
                plt.text(
                    i,
                    row['media'] * 1.01,
                    f"{row['media']:.2f}±{row['std']:.2f}\n(n={int(row['n'])})",
                    ha='center',
                    va='bottom',
                    fontsize=8
                )

        plt.xlabel('Dia Relativo')
        plt.ylabel('Valor Médio')
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