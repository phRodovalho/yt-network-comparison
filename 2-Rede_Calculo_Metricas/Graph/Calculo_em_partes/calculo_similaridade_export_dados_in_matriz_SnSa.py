import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import datetime

def cosine_similarity_sklearn(metr_chan1, metr_chan2):
    return cosine_similarity(metr_chan1, metr_chan2)

def main():
    timeFile = datetime.datetime.now().strftime("%d.%m_%Hh")
    output_directory_path = os.path.join(os.getcwd(), "output_similaridade_SnSa_" + timeFile)
    os.makedirs(output_directory_path, exist_ok=True)

    file_path = "C:\\Users\\pheli\\Desktop\\Comparar redes complexas\\DataTCC.csv"
    dados_canais = pd.read_csv(file_path)
    grupos = dados_canais['Grupo'].unique()

    # Dicionário para armazenar métricas de todos os canais
    all_metrics = {}

    for grupo in grupos:
        dados_grupo = dados_canais[dados_canais['Grupo'] == grupo]
        metricas = {}

        for _, canal in dados_grupo.iterrows():
            ch_name = canal['Canal']
            dados_selecionados = canal[['Degree', 'Closeness', 'Betweenness', 'Modularity', 'Density', 'Average clustering', 'Page Rank']].values
            metricas[ch_name] = np.array([dados_selecionados])
            all_metrics[ch_name] = np.array([dados_selecionados])

        canais = list(metricas.keys())
        similarity_matrix = np.zeros((len(canais), len(canais)))

        for i, ch1 in enumerate(canais):
            for j, ch2 in enumerate(canais):
                if i != j:
                    metr_chan1 = metricas[ch1]
                    metr_chan2 = metricas[ch2]
                    similaridadeCosseno = cosine_similarity_sklearn(metr_chan1, metr_chan2)
                    similarity_matrix[i, j] = similaridadeCosseno[0, 0]
                else:
                    similarity_matrix[i, j] = 1.0

        similarity_df = pd.DataFrame(similarity_matrix, index=canais, columns=canais)
        group_file_path = os.path.join(output_directory_path, f"similaridade_grupo_{grupo}.csv")
        similarity_df.to_csv(group_file_path)

    # Cálculo da similaridade entre todos os canais de todos os grupos
    all_canais = list(all_metrics.keys())
    all_similarity_matrix = np.zeros((len(all_canais), len(all_canais)))

    for i, ch1 in enumerate(all_canais):
        for j, ch2 in enumerate(all_canais):
            if i != j:
                metr_chan1 = all_metrics[ch1]
                metr_chan2 = all_metrics[ch2]
                similaridadeCosseno = cosine_similarity_sklearn(metr_chan1, metr_chan2)
                all_similarity_matrix[i, j] = similaridadeCosseno[0, 0]
            else:
                all_similarity_matrix[i, j] = 1.0

    all_similarity_df = pd.DataFrame(all_similarity_matrix, index=all_canais, columns=all_canais)
    all_similarity_path = os.path.join(output_directory_path, "resultadoSimilaridadeTodosGrupos.csv")
    all_similarity_df.to_csv(all_similarity_path)

if __name__ == "__main__":
    main()
