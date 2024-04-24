import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import datetime

def cosine_similarity_sklearn(metr_chan1, metr_chan2):
    return cosine_similarity(metr_chan1, metr_chan2)

def main():
    timeFile = datetime.datetime.now().strftime("%d.%m_%Hh")
    output_directory_path = os.path.join(os.getcwd(), "output_similaridade_" + timeFile)
    os.makedirs(output_directory_path, exist_ok=True)

    file_path = "C:\\Users\\pheli\\Desktop\\Comparar redes complexas\\DataTCC.csv"
    dados_canais = pd.read_csv(file_path)
    grupos = dados_canais['Grupo'].unique()
    
    # Inicializar DataFrame vazio para todos os grupos
    all_similarity_df = pd.DataFrame()

    for grupo in grupos:
        dados_grupo = dados_canais[dados_canais['Grupo'] == grupo]
        metricas = {}

        for _, canal in dados_grupo.iterrows():
            ch_name = canal['Canal']
            dados_selecionados = canal[['Qnt Nós C/PD', 'Qnt Arestas C/PD','Degree', 'Closeness', 'Betweenness', 'Modularity', 'Density', 'Average clustering', 'Page Rank']].values
            metricas[ch_name] = np.array([dados_selecionados])

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

        # Acumular a matriz de similaridade para todos os grupos
        if all_similarity_df.empty:
            all_similarity_df = similarity_df
        else:
            # Concatenar lado a lado (isso presume não haver canais duplicados entre grupos)
            all_similarity_df = pd.concat([all_similarity_df, similarity_df], axis=1)

    # Criar e salvar um CSV para todos os grupos
    all_similarity_path = os.path.join(output_directory_path, "resultadoSimilaridadeTodosGrupos.csv")
    all_similarity_df.to_csv(all_similarity_path)

if __name__ == "__main__":
    main()
