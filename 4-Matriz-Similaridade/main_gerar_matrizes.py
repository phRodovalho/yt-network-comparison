import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import pairwise_distances

def process_and_plot_similarity(file_path):
    # Carregar os dados do CSV em um DataFrame
    similarity_df = pd.read_csv(file_path, index_col=0)

    # Normalizando os dados para melhorar a visualização (se necessário)
    # Similaridade Pearson opcional, removida por enquanto
    #similarity_df = (similarity_df - similarity_df.min().min()) / (similarity_df.max().max() - similarity_df.min().min())
    
    # Ajustando o esquema de cores e os limites para melhor visualização
    plt.figure(figsize=(12, 10))
    ax = sns.heatmap(similarity_df, annot=True, fmt=".2f", cmap='YlGnBu', vmin=0.8, vmax=1)
    #plt.title(f'Matriz de Similaridade de Cosseno entre canais do Youtube')

    # Melhorar a visibilidade das anotações dependendo do valor de similaridade
    for text in ax.texts:
        t = float(text.get_text())
        if t > 0.95:
            text.set_weight('bold')
            text.set_color('white')
        elif t < 0.85:
            text.set_color('black')

    plt.show()

def process_directory(directory_path):
    # Lista todos os arquivos CSV no diretório especificado
    for file in os.listdir(directory_path):
        if file.endswith(".csv"):
            file_path = os.path.join(directory_path, file)
            process_and_plot_similarity(file_path)

if __name__ == "__main__":
    directory_path = "C:\\Users\\pheli\\Desktop\\Comparar redes complexas\\yt-network-comparison\\output_similaridade_SnSa_19.04_17h"
    process_directory(directory_path)
