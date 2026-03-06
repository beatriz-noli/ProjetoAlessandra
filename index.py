hemogramas.columns = hemogramas.columns.str.lower().str.strip()
sinais_vitais.columns = sinais_vitais.columns.str.lower().str.strip()

dados_paciente = {}

for coluna in hemogramas.columns:
    dados_paciente[coluna] = hemogramas[coluna].values[0]

for coluna in sinais_vitais.columns:
    dados_paciente[coluna] = sinais_vitais[coluna].values[0]

def consultar_parametro(parametro):
    parametro = parametro.lower().strip()
    hemogramas_para = hemogramas[hemogramas["parametro"] == parametro].assign(origem="hemogramas")
    sinais_vitais_para = sinais_vitais[sinais_vitais["parâmetro"] == parametro].assign(origem="sinais_vitais")

    df_para = pd.concat([hemogramas_para, sinais_vitais_para])

    if parametro in dados_paciente:
        print(f"{parametro.upper()}: {dados_paciente[parametro]}")
    else:
        print("Parâmetro não encontrado.")
    return df_para

consultar_parametro("Temperatura( °C )")
consultar_parametro("Microorganismos Isolados")
a = consultar_parametro("Temperatura( °C )")
a = consultar_parametro("Microorganismos Isolados")
