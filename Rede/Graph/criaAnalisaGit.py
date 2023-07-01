import os
import numpy as np 
import pandas as pd
import networkx as nx
from tkinter import  *
import scipy.stats as stats
from pyvis.network import Network
from sklearn.metrics.pairwise import cosine_similarity

def montar_rede(nodesList, edgesList):
    graph = nx.Graph()

    # adicionando os nos na rede
    for index, row in nodesList.iterrows():
        graph.add_node(row['Id'], label=row['Label'])

    # adicionando as arestas na rede
    for index, row in edgesList.iterrows():
        graph.add_edge(row['Source'] , row['Target'], weight=int(row['Profundidade']))

    return graph


def createDir(nameDir):
    path = os.path.join(nameDir)
    try:
        os.mkdir(path)
        return path
    except OSError as error:
        print(error)
        return path


def metricas_comunidade(graph):
    # dicionario para salvar as metricas de comunidade
    metricasComunidade = {}

    # modularidade
    modularidade = nx.algorithms.community.modularity(graph, nx.algorithms.community.greedy_modularity_communities(graph))
    # normalizando a modularidade com zscore
    # criar array numpy
    modularidadearray = np.array([modularidade, modularidade])

    a = np.array([ 0.6826250621863962,  0.6826250621863987])
    modularidaderesult = stats.zscore(a)

    metricasComunidade['Modularidade'] = modularidade

    # densidade
    densidade = nx.density(graph)
    # normalizando a densidade com zscore
    densidade = stats.zscore([densidade])
    metricasComunidade['Densidade'] = densidade

    # coeficiente de agrupamento
    coefAgrupamento = nx.average_clustering(graph)
    # normalizando o coeficiente de agrupamento com zscore
    coefAgrupamento = stats.zscore([coefAgrupamento])
    metricasComunidade['Coeficiente de Agrupamento'] = coefAgrupamento

    return metricasComunidade


def metricas_centralidade(graph):
    # dicionario para salvar as metricas de centralidade
    metricasCentralidade = {}

    # centralidade de grau
    centralidadeGrau = nx.degree_centrality(graph)

    # centralidade de proximidade
    centralidadeProximidade = nx.closeness_centrality(graph)

    # centralidade de intermediacao
    centralidadeIntermediacao = nx.betweenness_centrality(graph)

    # para cada no, montar um np.array com as metricas de centralidade e adicionar ao dicionario
    for node in graph.nodes:
        metricasCentralidade[node] = np.array([centralidadeGrau[node], centralidadeProximidade[node], centralidadeIntermediacao[node]])
    
    return metricasCentralidade


def metricas_global(graph):
    # dicionario para salvar as metricas globais
    metricasGlobal = {}

    # diametro
    diametro = nx.algorithms.distance_measures.diameter(graph)
    # normalizando o diametro com zscore
    diametro = stats.zscore([diametro])
    metricasGlobal['Diametro'] = diametro

    # raio
    raio = nx.radius(graph)
    # normalizando o raio com zscore
    raio = stats.zscore([raio])
    metricasGlobal['Raio'] = raio

    # densidade
    densidade = nx.density(graph)
    # normalizando a densidade com zscore
    densidade = stats.zscore([densidade])
    metricasGlobal['Densidade'] = densidade

    # quantidade de nos
    qtdNos = graph.number_of_nodes()
    # normalizando a quantidade de nos com zscore
    qtdNos = stats.zscore([qtdNos])
    metricasGlobal['Quantidade de Nos'] = qtdNos

    # quantidade de arestas
    qtdArestas = graph.number_of_edges()
    # normalizando a quantidade de arestas com zscore
    qtdArestas = stats.zscore([qtdArestas])
    metricasGlobal['Quantidade de Arestas'] = qtdArestas

    return metricasGlobal


def distancia_euclidiana(graph1, graph2):
    # distancia euclidiana entre dois vetores
    distanciaEuclidianaRede1 = nx.floyd_warshall_numpy(graph1)
    print(distanciaEuclidianaRede1)

    distanciaEuclidianaRede2 = nx.floyd_warshall_numpy(graph2)
    print(distanciaEuclidianaRede2)


def cosine_similarity_sklearn(dictMetricas):
    # percorrer o dicionario
    arrayMetricas1 = dictMetricas['UChYkldqKWymAKTsPku_tDfg']
    arrayMetricas2 = dictMetricas['UCY26QBG77UjscEC6dig8AYw']
    
    # Converter os arrays de 1D para uma matriz 2D
    matrizMetricas = np.vstack((arrayMetricas1, arrayMetricas2))

    # calcular a similaridade de cosseno entre os dois arrays
    similaridadeCosseno = cosine_similarity(matrizMetricas)
    print(similaridadeCosseno)

    # salvar em um arquivo txt  
    file = open("similaridadeCosseno.txt", "w")
    file.write(str(similaridadeCosseno))
    file.close()




def carregar_dados(path):
    pathNodes = path + "\\Nos.csv"
    pathEdges = path + "\\Arestas.csv"

    nodesList = pd.read_csv(pathNodes)
    edgesList = pd.read_csv(pathEdges)

    return nodesList, edgesList


def main():
    # Algoritmo de análise de redes complexas, com o objetivo de comparar redes de canais do YouTube
    # Passo 1. Acessar os dados dos canais e criar lista de arestas e nós para cada canal
    nodesCh01, edgesCh01 = carregar_dados("ColetaDeDados\\canal-1-gl")
    nodesCh02, edgesCh02 = carregar_dados("ColetaDeDados\\canal-2-l")

    # Passo 2. Criar um grafo para cada canal
    graph1 = montar_rede(nodesCh01, edgesCh01)
    #graph2 = montar_rede(nodesCh02, edgesCh02)

    # Passo 3. Comparação das redes dos canais através de métricas
    # Métricas de comunidade (modularidade, densidade, coeficiente de agrupamento)
    # metricasComunidade1 = metricas_comunidade(graph1)
    # metricasComunidade2 = metricas_comunidade(graph2)

    # Métricas de centralidade (centralidade de grau, centralidade de proximidade)
    metricas_centralidade1 = metricas_centralidade(graph1)
    #metricas_centralidade2 = metricas_centralidade(graph2)

    # Métricas globais (diametro, raio, densidade)
    # metricas_global1 = metricas_global(graph1)
    # metricas_global2 = metricas_global(graph2)

    # comparar medida de similaridade entre as redes distancia euclidiana ou similaridade de cosseno
    # distancia_euclidiana(graph1, graph2)

    # similaridade de cosseno com sklearn
    cosine_similarity_sklearn(metricas_centralidade1)  

    # Passo 4. Apresentar o resultado da comparação em CSV






main()