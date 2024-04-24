"""
Social Network System - Sistema de comparação de canais do Youtube
por meio de redes complexas.

A ser desenvolvido:
1. Coleta de dados de dois canais do Youtube
   Será exportado arquivos .CSV com os dados de cada canal para ser usado no Gephi
   A coleta de dados será feita por meio da API do Youtube.
2. Montagem da rede dos canais a partir dos dados coletados
   A definir como será montado essa rede, inicialmente será feito por meio da
    biblioteca NetworkX.
   Será montada uma rede complexa a partir dos dados coletados.
   Visualização das redes de cada canal
3. Comparação das redes dos canais 1 e 2 por meio de métricas
   Comunidade, Centralidade, Global, Caminhos.
4. Apresentar o resultado da comparação juntamente com a visualização das redes.
"""


import networkx as nx
import pandas as pd
from pyvis.network import Network
import scipy.stats as stats
from tkinter import *
import os
import numpy as np


def montar_rede(pathChannel, nameChannel):
    pathNodes = pathChannel + "\\Nos.csv"
    pathEdges = pathChannel + "\\Arestas.csv"
    
    graph = nx.DiGraph(name=nameChannel)
    
    # read the csv file
    nodesList = pd.read_csv(pathNodes)
    # adicionando os nos na rede
    for index, row in nodesList.iterrows():
        graph.add_node(row['Id'], label=row['Label'], title=row['Label'])

    # read the csv file
    edgesList = pd.read_csv(pathEdges)

    # adicionando as arestas na rede
    edgesList = pd.read_csv(pathEdges)
    edge_attrs = {
        'NomeCanalSeguidor': edgesList['NomeCanalSeguidor'],
        'NomeCanalSeguido': edgesList['NomeCanalSeguido'],
        'Descricao': edgesList['Descricao'],
        'DataPublicacao': edgesList['DataPublicacao'],
        'Profundidade': edgesList['Profundidade'].astype(int),
        'Type': edgesList['Type']
    }
    edges = [(row['Source'], row['Target'], {k: attrs[i] for k, attrs in edge_attrs.items()}) for i, row in edgesList.iterrows()]
    graph.add_edges_from(edges)

    return graph

def montar_rede_strong(pathChannel, nameChannel):
    pathNodes = pathChannel + "\\Nos.csv"
    pathEdges = pathChannel + "\\Arestas.csv"
    graphs = []

    # read the csv file
    nodesList = pd.read_csv(pathNodes)

    # adicionando nome do canal na rede
    # cada componente conectado terá um nome diferente
    channel_name = nameChannel + "_componente_"

    # adicionando os nos na rede
    for index, row in nodesList.iterrows():
        graph = nx.DiGraph()
        graph.add_node(row['Id'], label=row['Label'], title=row['Label'])
        graphs.append(graph)

    # read the csv file
    edgesList = pd.read_csv(pathEdges)

    # adicionando as arestas na rede
    edge_attrs = {
        'NomeCanalSeguidor': '',
        'NomeCanalSeguido': '',
        'Descricao': '',
        'DataPublicacao': '',
        'Profundidade': '',
        'Type': ''
    }

    for index, row in edgesList.iterrows():
        attrs = edge_attrs.copy()
        attrs['NomeCanalSeguidor'] = row['NomeCanalSeguidor']
        attrs['NomeCanalSeguido'] = row['NomeCanalSeguido']
        attrs['Descricao'] = row['Descricao']
        attrs['DataPublicacao'] = row['DataPublicacao']
        attrs['Profundidade'] = int(row['Profundidade'])
        attrs['Type'] = row['Type']
        source_id = row['Source']
        target_id = row['Target']
        for graph in graphs:
            if source_id in graph.nodes and target_id in graph.nodes:
                graph.add_edge(source_id, target_id, **attrs)

    # renomeando os grafos com o nome do canal e o componente
    for i, graph in enumerate(graphs):
        graph.name = channel_name + str(i+1)
    return graphs


def drawing_network(graph, name):
    # Draw the network using Pyvis
    net = Network(notebook=True)
    net.from_nx(graph)
    net.show_buttons(filter_=['nodes', 'edges', 'physics', 'selection'])
    net.force_atlas_2based()
    
    
    pathFile = "C:\\Users\\pheli\\Desktop\\Comparar redes complexas\\" + name
    try:
        net.show(pathFile + "\\" + name + ".html")
    except:
        path = createDir(pathFile)
        net.show(name + ".html")

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
    modularidade = nx.algorithms.community.modularity(
        graph, nx.algorithms.community.greedy_modularity_communities(graph))
    # normalizando a modularidade com zscore
    # criar array numpy
    modularidadearray = np.array([modularidade, modularidade])

    a = np.array([0.6826250621863962,  0.6826250621863987])
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
    # media das centralidades de grau
    CentralidadeGrau = sum(centralidadeGrau.values()) / len(centralidadeGrau)
    # normalizando a centralidade de grau com zscore
    CentralidadeGrau = stats.zscore([CentralidadeGrau])
    metricasCentralidade['Centralidade-De-Grau'] = CentralidadeGrau

    # centralidade de proximidade
    centralidadeProximidade = nx.closeness_centrality(graph)
    # media das centralidades de proximidade
    CentralidadeProximidade = sum(
        centralidadeProximidade.values()) / len(centralidadeProximidade)
    # normalizando a centralidade de proximidade com zscore
    CentralidadeProximidade = stats.zscore([CentralidadeProximidade])
    metricasCentralidade['Centralidade-De-Proximidade'] = CentralidadeProximidade

    # centralidade de intermediacao
    centralidadeIntermediacao = nx.betweenness_centrality(graph)
    # media das centralidades de intermediacao
    CentralidadeIntermediacao = sum(
        centralidadeIntermediacao.values()) / len(centralidadeIntermediacao)
    # normalizando a centralidade de intermediacao com zscore
    CentralidadeIntermediacao = stats.zscore([CentralidadeIntermediacao])
    metricasCentralidade['Centralidade-De-Intermediacao'] = CentralidadeIntermediacao

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


def main():
    # Passo 1. Coleta de dados de dois canais do Youtube
    # execute o script CollectDataCreateNetwork.py para coletar os dados dos canais e criar a rede complexa
    # CollectDataNetwork.main()

    # Passo 2. Montagem da rede dos canais a partir dos dados coletados
    #pathChannel01 = "ColetaDeDados\Bruno e Marrone"
    pathChannel01 = "ColetaDeDados\Leonardo"
    graph1 = montar_rede(pathChannel01, "Leonardo")

    pathChannel02 = "C:\\TCC\\Network\\ColetaRedeComplexa_CSV\\Gustavo Lima"
    # pathChannel02 = "C:\\ChannelNetwork_Sertanejo\\Gustavo Lima"
    graph2 = montar_rede(pathChannel02, "Gustavo Lima")

    # Visualização das redes de cada canal
    #drawing_network(graph1, Network, graph1.name)
    #drawing_network(graph2, Network, graph2.name)

    # Passo 3. Comparação das redes dos canais 1 e 2 por meio de métricas
    # Métricas de comunidade (modularidade, densidade, coeficiente de agrupamento)
    metricasComunidade1 = metricas_comunidade(graph1)
    metricasComunidade2 = metricas_comunidade(graph2)

    # Métricas de centralidade (centralidade de grau, centralidade de proximidade)
    metricas_centralidade1 = metricas_centralidade(graph1)
    metricas_centralidade2 = metricas_centralidade(graph2)

    # Métricas globais (diametro, raio, densidade)
    metricas_global1 = metricas_global(graph1)
    metricas_global2 = metricas_global(graph2)

    # comparar medida de similaridade entre as redes distancia euclidiana ou similaridade de cosseno
    distancia_euclidiana(graph1, graph2)

    # Passo 4. Apresentar o resultado da comparação juntamente com a visualização das redes.
    print("Métricas de Comunidade")
    print("Rede 1: ", metricasComunidade1)
    print("Rede 2: ", metricasComunidade2)

    print("Métricas de Centralidade")
    print("Rede 1: ", metricas_centralidade1)
    print("Rede 2: ", metricas_centralidade2)

    print("Métricas Globais")
    print("Rede 1: ", metricas_global1)
    print("Rede 2: ", metricas_global2)

    


main()
