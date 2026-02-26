import pandas as pd
import os

hemogramas = pd.read_excel("tabelas/hemogramas.xlsx")
sinais_vitais = pd.read_excel("tabelas/sinais_vitais.xlsx")

hemogramas.columns = hemogramas.columns.str.lower().str.strip()
sinais_vitais.columns = sinais_vitais.columns.str.lower().str.strip()

dados_paciente = {}

for coluna in hemogramas.columns:
    dados_paciente[coluna] = hemogramas[coluna].values[0]

for coluna in sinais_vitais.columns:
    dados_paciente[coluna] = sinais_vitais[coluna].values[0]

def consultar_parametro(parametro):
    parametro = parametro.lower().strip()
    
    if parametro in dados_paciente:
        print(f"{parametro.upper()}: {dados_paciente[parametro]}")
    else:
        print("Parâmetro não encontrado.")

consultar_parametro("Temperatura( °C )")
consultar_parametro("Microorganismos Isolados")