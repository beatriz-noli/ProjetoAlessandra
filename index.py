import pandas as pd
import os

hemogramas = pd.read_excel("tabelas/hemogramas.xlsx")
sinais_vitais = pd.read_excel("tabelas/sinais_vitais.xlsx")

hemogramas.columns = hemogramas.columns.str.lower().str.strip()
sinais_vitais.columns = sinais_vitais.columns.str.lower().str.strip()

def consultar_parametro(parametro):
    hemogramas_para = hemogramas[hemogramas["parametro"] == parametro].assign(origem="hemogramas")
    sinais_vitais_para = sinais_vitais[sinais_vitais["parâmetro"] == parametro].assign(origem="sinais_vitais")

    df_para = pd.concat([hemogramas_para, sinais_vitais_para])
    
    return df_para

a = consultar_parametro("Temperatura( °C )")
a = consultar_parametro("Microorganismos Isolados")
