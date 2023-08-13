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

    # TODO: pagerank

    # centralidade de grau
    centralidadeGrau = nx.degree_centrality(graph)

    # centralidade de proximidade
    centralidadeProximidade = nx.closeness_centrality(graph, wf_improved=False)

    # centralidade de intermediacao
    centralidadeIntermediacao = nx.betweenness_centrality(graph)

    # para cada no, montar um np.array com as metricas de centralidade e adicionar ao dicionario
    for node in graph.nodes:
        metricasCentralidade[node] = np.array([[centralidadeGrau[node], centralidadeProximidade[node], centralidadeIntermediacao[node]]])
    
    return metricasCentralidade


def metricas_global(graph):
    # dicionario para salvar as metricas globais
    metricasGlobal = {}

    # diametro
    #diametro = nx.algorithms.distance_measures.diameter(graph)
    # normalizando o diametro com zscore
    #diametro = stats.zscore([diametro])
    # metricasGlobal['Diametro'] = diametro

    # raio
    #raio = nx.radius(graph)
    # normalizando o raio com zscore
    #raio = stats.zscore([raio])
    #metricasGlobal['Raio'] = raio

    # densidade
    densidade = nx.density(graph)
    # normalizando a densidade com zscore
    #densidade = stats.zscore([densidade])
    metricasGlobal['Densidade'] = densidade

    # quantidade de nos
    qtdNos = graph.number_of_nodes()
    # normalizando a quantidade de nos com zscore
    #qtdNos = stats.zscore([qtdNos])
    metricasGlobal['Quantidade de Nos'] = qtdNos

    # quantidade de arestas
    qtdArestas = graph.number_of_edges()
    # normalizando a quantidade de arestas com zscore
    # qtdArestas = stats.zscore([qtdArestas])
    metricasGlobal['Quantidade de Arestas'] = qtdArestas

    return metricasGlobal


def distancia_euclidiana(graph1, graph2):
    # distancia euclidiana entre dois vetores
    distanciaEuclidianaRede1 = nx.floyd_warshall_numpy(graph1)
    print(distanciaEuclidianaRede1)

    distanciaEuclidianaRede2 = nx.floyd_warshall_numpy(graph2)
    print(distanciaEuclidianaRede2)


def cosine_similarity_sklearn(dict1, key1, dict2, key2):
    # percorrer o dicionario
    arrayMetricas1 = dict1[key1]
    arrayMetricas2 = dict2[key2]
    
    # calcular a similaridade de cosseno entre os dois arrays
    similaridadeCosseno = cosine_similarity(arrayMetricas1, arrayMetricas2)

    return similaridadeCosseno

def salvar_similaridade_cosseno(text, similaridadeCosseno):
    # salvar em um arquivo txt  
    file = open("similaridadeCosseno.txt", "a")
    file.write(text + str(similaridadeCosseno))
    file.close()

def carregar_dados(path):
    pathNodes = path + "\\Nos.csv"
    pathEdges = path + "\\Arestas.csv"

    nodesList = pd.read_csv(pathNodes)
    edgesList = pd.read_csv(pathEdges)

    return nodesList, edgesList

def remover_nos_folhas(graph):
    # criar lista com os nos folhas
    nosFolhas = [node for node, degree in dict(graph.degree()).items() if degree == 1]
    # remover os nos folhas
    graph.remove_nodes_from(nosFolhas)
    return graph

def main():
    # Algoritmo de análise de redes complexas, com o objetivo de comparar redes de canais do YouTube
    # Passo 1. Acessar os dados dos canais e criar lista de arestas e nós para cada canal
    nodesCh01, edgesCh01 = carregar_dados("ColetaDeDados\\PablloVitar")
    nodesCh02, edgesCh02 = carregar_dados("ColetaDeDados\\GloriaGroove")
    nodesCh03, edgesCh03 = carregar_dados("ColetaDeDados\\canal-1-gl") 
    nodesCh04, edgesCh04 = carregar_dados("ColetaDeDados\\canal-2-l")

    # Passo 2. Criar um grafo para cada canal
    #graphPablloVitar = montar_rede(nodesCh01, edgesCh01)
    #graphGloriaGroover = montar_rede(nodesCh02, edgesCh02)
    #graphGustavoLima = montar_rede(nodesCh03, edgesCh03)
    graphLeonardo = montar_rede(nodesCh04, edgesCh04)

    # TODO: numero de nos e arestas de cada grafo antes de remover os nos folhas
    print("Numeros de nos antes da poda: ", graphLeonardo.number_of_nodes())

    # removendo os nos folhas 
    #graphPablloVitar = remover_nos_folhas(graphPablloVitar)
    #graphGloriaGroover = remover_nos_folhas(graphGloriaGroover)
    #graphGustavoLima = remover_nos_folhas(graphGustavoLima)
    graphLeonardo = remover_nos_folhas(graphLeonardo)

    # TODO: numero de nos e arestas de cada grafo depois de remover os nos folhas
    print("Numeros de nos depois da poda: ", graphLeonardo.number_of_nodes())

    # TODO: salvar os grafos em um arquivo .gexf
    # TODO: gerar html com os grafos

    
    # TODO: comparar redes de pessoas publicas e pessoas comuns
    # TODO: contar quantidade de pessoas seguidas e as que não per

    # Passo 3. Comparação das redes dos canais através de métricas
    # Métricas de comunidade (modularidade, densidade, coeficiente de agrupamento)
    # metricasComunidade1 = metricas_comunidade(graph1)
    # metricasComunidade2 = metricas_comunidade(graph2)

    # Métricas de centralidade (centralidade de grau, centralidade de proximidade)
    #met_centPablloVitar = metricas_centralidade(graphPablloVitar)
    #met_centGloriaGroover = metricas_centralidade(graphGloriaGroover)
    #met_centGustavoLima = metricas_centralidade(graphGustavoLima)
    met_centLeonardo = metricas_centralidade(graphLeonardo)
    print(met_centLeonardo)

    # Métricas globais (diametro, raio, densidade)
    metricas_global1 = metricas_global(graphLeonardo)
    # metricas_global2 = metricas_global(graph2)

    # comparar medida de similaridade entre as redes distancia euclidiana ou similaridade de cosseno
    # distancia_euclidiana(graph1, graph2)

    # similaridade de cosseno com sklearn
    #salvar resultado em um dict
    #simGL_L = cosine_similarity_sklearn(met_centGustavoLima, "UCXooz9whNJZBRTHi9AqdjPw", met_centLeonardo, "UC-kCNs2KVMx0WN-tfysYTIw")  
    #simGL_P = cosine_similarity_sklearn(met_centGustavoLima, "UCXooz9whNJZBRTHi9AqdjPw", met_centPablloVitar, "UCugD1HAP3INAiXo70S_sAFQ")  
    #simGL_GG = cosine_similarity_sklearn(met_centGustavoLima, "UCXooz9whNJZBRTHi9AqdjPw", met_centGloriaGroover, "UCLoL96fSeaLOen3mpDYeqtA")  
    #simL_P = cosine_similarity_sklearn(met_centLeonardo,"UC-kCNs2KVMx0WN-tfysYTIw", met_centPablloVitar, "UCugD1HAP3INAiXo70S_sAFQ")  
    #simL_GG = cosine_similarity_sklearn(met_centLeonardo, "UC-kCNs2KVMx0WN-tfysYTIw", met_centGloriaGroover, "UCLoL96fSeaLOen3mpDYeqtA")  
    #simP_GG = cosine_similarity_sklearn(met_centPablloVitar, "UCugD1HAP3INAiXo70S_sAFQ", met_centGloriaGroover, "UCLoL96fSeaLOen3mpDYeqtA")  
    
    #print(simGL_L)
    #print(simGL_P)
    #print(simL_P)
    #print(simGL_GG)
    #print(simL_GG)
    #print(simP_GG)

    # Passo 4. Apresentar o resultado da comparação em CSV
    # salvar em um arquivo txt
    #salvar_similaridade_cosseno("Similaridade entre Gustavo Lima e Leonardo: ", simGL_L)
    #salvar_similaridade_cosseno("Similaridade entre Gustavo Lima e Pabllo Vitar: ", simGL_P)
    #salvar_similaridade_cosseno("Similaridade entre Gustavo Lima e Gloria Groove: ", simGL_GG)
    #salvar_similaridade_cosseno("Similaridade entre Leonardo e Pabllo Vitar: ", simL_P)
    #salvar_similaridade_cosseno("Similaridade entre Leonardo e Gloria Groove: ", simL_GG)
    #salvar_similaridade_cosseno("Similaridade entre Pabllo Vitar e Gloria Groove: ", simP_GG)


 # criar um dicionario com os dados abaixo
   
#["UCLoL96fSeaLOen3mpDYeqtA", "GloriaGroover"]
#["UCugD1HAP3INAiXo70S_sAFQ", "Pabllo Vittar"]
#["UC-kCNs2KVMx0WN-tfysYTIw", "Leonardo"]
#["UCXooz9whNJZBRTHi9AqdjPw", "Gustavo Lima"]







main()