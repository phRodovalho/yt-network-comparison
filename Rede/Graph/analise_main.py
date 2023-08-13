import configparser
import os
import numpy as np 
import pandas as pd
import networkx as nx
from tkinter import  *
import scipy.stats as stats
from pyvis.network import Network
from sklearn.metrics.pairwise import cosine_similarity
import datetime

output_path = os.path.join(os.getcwd(), "graph_statistics.txt")

def load_config():
    config = configparser.ConfigParser()
    config.read("C:\\Users\\pheli\\Desktop\\Comparar redes complexas\\yt-network-comparison\\Rede\\Graph\\config.ini")
    return config

def get_file_paths(path):
    path_nodes = os.path.join(path, "Nos.csv")
    path_edges = os.path.join(path, "Arestas.csv")
    return path_nodes, path_edges

def load_data(pathNodes, pathEdges):
    nodesList = pd.read_csv(pathNodes)
    edgesList = pd.read_csv(pathEdges)
    return nodesList, edgesList

def build_graph(nodes_list, edges_list):
    graph = nx.Graph()
    for _, row in nodes_list.iterrows():
        graph.add_node(row['Id'], label=row['Label'])
    for _, row in edges_list.iterrows():
        graph.add_edge(row['Source'] , row['Target'], weight=int(row['Profundidade']))
    return graph

def save_graph_statistics(channelName, graph, output_path, op):
    num_nodes = graph.number_of_nodes()
    num_edges = graph.number_of_edges()
    formatted_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    if op == -1:
        with open(output_path, "a") as output_file:
            output_file.write("---- {} ----\n".format(formatted_time))
            output_file.write("Canal {}, ANTES de podar os nós folhas\n".format(channelName))
            output_file.write("Número de nós: {}\n".format(num_nodes))
            output_file.write("Número de arestas: {}\n".format(num_edges))
    elif op == 1:
        with open(output_path, "a") as output_file:
            output_file.write("---- {} ----\n".format(formatted_time))
            output_file.write("Canal {}, DEPOIS de podar os nós folhas\n".format(channelName))
            output_file.write("Número de nós: {}\n".format(num_nodes))
            output_file.write("Número de arestas: {}\n".format(num_edges))

def remove_leaf_nodes(graph):
    leaf_nodes = [node for node, degree in graph.degree() if degree == 1]
    graph.remove_nodes_from(leaf_nodes)
    return graph

def metricas_centralidade(graph):
    metricasCentralidade = {}

    centralidadeGrau = nx.degree_centrality(graph)
    centralidadeProximidade = nx.closeness_centrality(graph, wf_improved=False)
    centralidadeIntermediacao = nx.betweenness_centrality(graph)
    for node in graph.nodes:
        metricasCentralidade[node] = np.array([[centralidadeGrau[node], 
                                                centralidadeProximidade[node], 
                                                centralidadeIntermediacao[node]]])
    return metricasCentralidade

def metricas_globais(graph):
    modularidade = nx.algorithms.community.modularity(graph, nx.algorithms.community.greedy_modularity_communities(graph))
    communities = nx.algorithms.community.greedy_modularity_communities(graph)
    modularity = nx.algorithms.community.modularity(graph, communities)
    densidade = nx.density(graph)
    #diametro = nx.diameter(graph)
    num_nodes = graph.number_of_nodes()
    num_edges = graph.number_of_edges()

    return np.array([[modularidade, densidade, num_nodes, num_edges, modularity]])

def main():
    config = load_config()

    for chName, path in config.items("paths"):
        nodes_path, edges_path = get_file_paths(path)
        nodes_list, edges_list = load_data(nodes_path, edges_path)
        graph = build_graph(nodes_list, edges_list)
        save_graph_statistics(chName, graph, output_path, -1) 
        remove_leaf_nodes(graph)
        save_graph_statistics(chName, graph, output_path, 1) 
        
        #TODO: Organizar metricas
        metricas = metricas_centralidade(graph)
        print(metricas)
        metricaGlobal = metricas_globais(graph)
        print(metricaGlobal)


# TODO: salvar os grafos em um arquivo .gexf
# TODO: gerar html com os grafos

# TODO COLETA: contar quantidade de pessoas seguidas e as que não permitem visualizar
# TODO COLETA: comparar redes de pessoas publicas e pessoas comuns

if __name__ == "__main__":
    main()