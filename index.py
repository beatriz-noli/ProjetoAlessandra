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

Tabela_sinais = pd.concat(
    (
        pd.read_excel(xls_sinais, sheet_name=aba, header=0)
        for aba in abas_filtradas_sinais
    ),
    ignore_index=True
)


#%% Limpeza inicial
Tabela_hemogramas.dropna(how="all", inplace=True)
Tabela_sinais.dropna(how="all", inplace=True)

#%% Processamento Hemogramas

for col in Tabela_hemogramas.columns:
        if Tabela_hemogramas[col].dtype == "object" or pd.api.types.is_string_dtype(Tabela_hemogramas[col]):
            Tabela_hemogramas[col] = Tabela_hemogramas[col].str.strip()

# 📅 Criar datetime
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
    Tabela_sinais["Data"].astype(str) + " " + Tabela_sinais["Hora"].astype(str),
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce"
)

Tabela_sinais.drop(columns=["Data", "Hora"], inplace=True)

Tabela_sinais["Valor"] = pd.to_numeric( Tabela_sinais["Valor"], errors="coerce" )

# Otimizar dtypes
Tabela_sinais = Tabela_sinais.convert_dtypes()

# Dia relativo por paciente

Tabela_sinais["DIARELATIVO"] = (
    Tabela_sinais["DATETIME"] -
    Tabela_sinais.groupby("Paciente")["DATETIME"].transform("min")
).dt.days + 1


Tabela_hemogramas_pivot_NUMERICO = Tabela_hemogramas.pivot_table(
    index=['PACIENTE', 'DIARELATIVO'],
    columns=['EXAME', 'PARAMETRO'],
    values='VALOR NUMÉRICO',
    aggfunc='first'
)

Tabela_hemogramas_pivot_CATEGORICO = Tabela_hemogramas.pivot_table(
    index=['PACIENTE', 'DIARELATIVO'],
    columns=['EXAME', 'PARAMETRO'],
    values='VALOR CATEGÓRICO',
    aggfunc='first'
)