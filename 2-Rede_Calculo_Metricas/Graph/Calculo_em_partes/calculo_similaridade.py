import os
import time
import datetime
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from itertools import combinations

timeFile = datetime.datetime.now().strftime("%d.%m_%Hh")
output_file_path = os.path.join(os.getcwd(), "log_execucao_similaridade_"+ timeFile +"_.txt")
directory_path = os.path.join(os.getcwd())

def cosine_similarity_sklearn(metr_chan1, metr_chan2):
    similaridadeCosseno = cosine_similarity(metr_chan1, metr_chan2)
    return similaridadeCosseno

def save_file(msg, metrica):
    with open(output_file_path, "a", encoding='utf-8') as output_file:
        output_file.write(msg + " {}\n".format(metrica))

def main():
    file_path = "C:\\Users\\pheli\\Desktop\\Comparar redes complexas\\DataTCC.csv"
    dados_canais = pd.read_csv(file_path)
    metricas = {}

    for _, canal in dados_canais.iterrows():
        ch_name = canal['Canal']
        dados_selecionados = canal[['Degree', 'Closeness', 'Betweenness', 'Modularity', 'Density', 'Average clustering', 'Page Rank']].values
        metricas[ch_name] = np.array([dados_selecionados])

    resultado = {}
    for ch1, ch2 in combinations(metricas.keys(), 2):
        metr_chan1 = metricas[ch1]
        metr_chan2 = metricas[ch2]
        similaridadeCosseno = cosine_similarity_sklearn(metr_chan1, metr_chan2)
        save_file("Canal {} e Canal {} : ".format(ch1, ch2), similaridadeCosseno)
        canais_analisados_str = "Canal {} ; Canal {}".format(ch1, ch2)
        resultado[canais_analisados_str] = similaridadeCosseno[0,0]

    resultado_df = pd.DataFrame.from_dict(resultado, orient='index', columns=['Similaridade'])
    resultado_df.to_csv("C:\\Users\\pheli\\Desktop\\Comparar redes complexas\\resultadoSimilaridadeSemNosEArestas.csv")

if __name__ == "__main__":
    main()
