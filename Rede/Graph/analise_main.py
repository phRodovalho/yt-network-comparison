import os
import time
import datetime
import numpy as np 
import configparser
import pandas as pd
import networkx as nx
from pyvis.network import Network
from sklearn.metrics.pairwise import cosine_similarity

timeFile = datetime.datetime.now().strftime("%d.%m_%Hh%Mm")
output_file_path = os.path.join(os.getcwd(), "log_execucao_analises_redes_"+ timeFile +"_.txt")
directory_path = os.path.join(os.getcwd())

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

def build_graph(nodes_list, edges_list, channelName):
    graph = nx.Graph(name=channelName)
    for _, row in nodes_list.iterrows():
        graph.add_node(row['Id'], label=row['Label'], title=row['Label'])
    
    edge_attrs = {
        'NomeCanalSeguidor': edges_list['NomeCanalSeguidor'],
        'NomeCanalSeguido': edges_list['NomeCanalSeguido'],
        #'Descricao': edges_list['Descricao'],
        'DataPublicacao': edges_list['DataPublicacao'],
        'Profundidade': edges_list['Profundidade'].astype(int).tolist(),
        'Type': edges_list['Type']
    }
    edges = [
        (row['Source'], row['Target'], {k: attrs[i] for k, attrs in edge_attrs.items()})
        for i, row in edges_list.iterrows()
    ]
    graph.add_edges_from(edges)
    return graph

def drawing_network(graph):
    net = Network(notebook=False)
    net.from_nx(graph)
    net.show_buttons(filter_=['physics','interaction'])
    net.force_atlas_2based()
    return net

def export_network_gexf(graph, name, path, time_stamp):
    pathFile = os.path.join(path, f"rede_{name}_{time_stamp}_.gexf")
    nx.write_gexf(graph, pathFile)
    return True

def export_network_html(net, name, path, time_stamp):
    pathFile = os.path.join(path, f"rede_{name}_{time_stamp}_.html")
    try:
        net.save_graph(pathFile)
        return True
    except Exception as e:
        print(e)
        print("Erro ao gerar a rede do canal: " + name)
        return False

def save_node_edge_stats(channelName, graph, op):
    num_nodes = graph.number_of_nodes()
    num_edges = graph.number_of_edges()
    formatted_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    if op == -1:
        with open(output_file_path, "a") as output_file:
            output_file.write("\n\n---- {} ----\n".format(formatted_time))
            output_file.write("Canal {}, ANTES de podar os nós folhas\n".format(channelName))
            output_file.write("Número de nós: {}\n".format(num_nodes))
            output_file.write("Número de arestas: {}\n\n".format(num_edges))
    elif op == 1:
        with open(output_file_path, "a") as output_file:
            output_file.write("\n\n---- {} ----\n".format(formatted_time))
            output_file.write("Canal {}, DEPOIS de podar os nós folhas\n".format(channelName))
            output_file.write("Número de nós: {}\n".format(num_nodes))
            output_file.write("Número de arestas: {}\n\n".format(num_edges))

def save_file(msg, metrica):
    with open(output_file_path, "a") as output_file:
        output_file.write(msg + " {}\n".format(metrica))

def remove_leaf_nodes(graph):
    leaf_nodes = [node for node, degree in graph.degree() if degree == 1]
    graph.remove_nodes_from(leaf_nodes)
    return graph

def cosine_similarity_sklearn(metr_chan1, metr_chan2):
    similaridadeCosseno = cosine_similarity(metr_chan1, metr_chan2)
    return similaridadeCosseno

def get_channel_id(channelName, config):
  return config.get("ids", channelName)

def get_end_time(start_time):
    end_time = time.time()
    elapsed_time = (end_time - start_time)/60
    return elapsed_time

def main():
    start_time_programa = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    init_time_program = time.time()
    save_file(f"\n\n---- Iniciando Programa em {start_time_programa} ---- ", "")

    config = load_config()
    metricas = {}

    for chName, path in config.items("paths"):
        save_file(f"\n---- Iniciando Processamento do canal {chName} ---- ", "")
        save_file("---- Criando Grafo, construindo a rede ---- ", "")
        start_time_processamento = time.time()

        chId = get_channel_id(chName, config)
        nodes_path, edges_path = get_file_paths(path)
        nodes_list, edges_list = load_data(nodes_path, edges_path)
        graph = build_graph(nodes_list, edges_list, chName)

        save_node_edge_stats(chName, graph, -1) 
        remove_leaf_nodes(graph)
        save_node_edge_stats(chName, graph, 1)
        save_file(f"\n---- Canal {chName} processado em  {get_end_time(start_time_processamento)} minutos ---- ", "")
        
        save_file(f"\n---- Iniciando Calculo das métricas, canal {chName} ---- ", "")
        start_time_metricas = time.time()
        degree = nx.degree_centrality(graph)
        closeness = nx.closeness_centrality(graph, wf_improved=False)
        between = nx.betweenness_centrality(graph)
        pagerank = nx.pagerank(graph)
        modularity = nx.algorithms.community.modularity(graph, nx.algorithms.community.greedy_modularity_communities(graph))
        density = nx.density(graph)
        averClustering = nx.average_clustering(graph)
        num_nodes = graph.number_of_nodes()
        num_edges = graph.number_of_edges()
        save_file("---- Metricas ---- ", chName)
        save_file("degree_centrality : ", degree[chId])
        save_file("closeness_centrality : ", closeness[chId])
        save_file("betweenness_centrality : ", between[chId])
        save_file("modularity : ", modularity)
        save_file("density : ", density)
        save_file("average_clustering : ", averClustering)
        save_file("num_nodes : ", num_nodes)
        save_file("num_edges : ", num_edges)
        save_file("pagerank : ", pagerank[chId])
        save_file(f"\n---- Canal {chName}, métricas calculadas em  {get_end_time(start_time_metricas)} minutos ---- ", "")

        metricas[chName] = np.array([[degree[chId],
                              closeness[chId],
                              between[chId],
                              modularity,
                              density,
                              averClustering,
                              num_nodes,
                              num_edges,
                              pagerank[chId]]])
        
        save_file(f"\n---- Gerando arquivos de visualização do canal {chName} ---- ", "")
        start_time_visualizacao = time.time()
        time_stamp_files = datetime.datetime.now().strftime("%d_%m_%Y__%Hh%Mm")
        network = drawing_network(graph)
        export_network_html(network, chName, path, time_stamp_files)
        export_network_gexf(graph, chName, path, time_stamp_files)
        save_file(f"\n---- Canal {chName}, arquivos de visualização gerados em {get_end_time(start_time_visualizacao)} ---- ", "")
        save_file(f"\n---- Canal {chName} finalizado em {get_end_time(start_time_processamento)} minutos ---- ", "")

    save_file("\n---- Iniciando calculo da Similaridade entre todos canais analisados ---- ", "")
    for ch1, metr_chan1 in metricas.items():
        for ch2, metr_chan2 in metricas.items():
            if ch1 != ch2:
                similaridadeCosseno = cosine_similarity_sklearn(metr_chan1, metr_chan2)
                save_file("Canal {} e Canal {} : ".format(ch1, ch2), similaridadeCosseno)
    
    save_file(f"\n---- Similariadade calculada em {get_end_time(start_time_processamento)} minutos ---- ", "")
    save_file(f"\n---- Fim do Programa! Execução levou {get_end_time(init_time_program)} minutos ---- ", "")

if __name__ == "__main__":
    main()