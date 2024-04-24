import networkx as nx
import pandas as pd
from pyvis.network import Network
import scipy.stats as stats
from tkinter import *
import os
import numpy as np
import csv

print(nx.__version__)

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

def calcular_metricas_componentes2(graphs):
    metricas = {}
    for i, graph in enumerate(graphs):
        componentes = nx.strongly_connected_components(graph)
        for j, comp in enumerate(componentes):
            subgraph = graph.subgraph(comp)
            metricas_subgraph = {}
            metricas_subgraph['diametro'] = nx.algorithms.distance_measures.diameter(subgraph)
            metricas_subgraph['densidade'] = nx.density(subgraph)
            metricas_subgraph['centralidade_grau'] = dict(nx.algorithms.centrality.degree_centrality(subgraph))
            metricas_subgraph['centralidade_intermediacao'] = dict(nx.algorithms.centrality.betweenness_centrality(subgraph))
            if len(comp) > 1:
                comunidades = nx.algorithms.community.modularity_max.greedy_modularity_communities(subgraph)
                if comunidades:
                    metricas_subgraph['comunidades'] = dict(comunidades)
                else:
                    metricas_subgraph['comunidades'] = None
            else:
                metricas_subgraph['comunidades'] = None

            metricas[f'componente_{i}_{j}'] = metricas_subgraph
    return metricas

def calcular_metricas_globais(graph, components):
    metrics_global = {}
    metrics_components = []

    for i, component in enumerate(components):
        for j, subgraph_nodes in enumerate(component):
            # ignore invalid components
            if len(subgraph_nodes) == 0:
                continue
            
            subgraph = graph[i].subgraph(subgraph_nodes)
            metrics = calcular_metricas_componentes2([subgraph])
            metrics_components.append(metrics[f'componente_{i}_{j}'])
            
            for metric, value in metrics[f'componente_{i}_{j}'].items():
                if metric in metrics_global:
                    metrics_global[metric] += value
                else:
                    metrics_global[metric] = value
    
    for metric, value in metrics_global.items():
        metrics_global[metric] = value / len(metrics_components)
        
    metrics_global['componentes'] = metrics_components
    
    return metrics_global

def save_metrics_to_csv(global_metrics1, component_metrics1, global_metrics2, component_metrics2, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Escrever o cabeçalho do arquivo
        writer.writerow(['Graph', 'Metric', 'Value'])
        
        # Escrever as métricas do primeiro grafo
        for metric_name, metric_value in global_metrics1.items():
            writer.writerow(['Channel 01 (Global)', metric_name, metric_value])
        for component_id, component_metrics in component_metrics1.items():
            for metric_name, metric_value in component_metrics.items():
                writer.writerow(['Channel 01 (Component {})'.format(component_id), metric_name, metric_value])
        
        # Escrever as métricas do segundo grafo
        for metric_name, metric_value in global_metrics2.items():
            writer.writerow(['Channel 02 (Global)', metric_name, metric_value])
        for component_id, component_metrics in component_metrics2.items():
            for metric_name, metric_value in component_metrics.items():
                writer.writerow(['Channel 02 (Component {})'.format(component_id), metric_name, metric_value])
                
        print('Métricas salvas em {}'.format(filename))

def main():
    nameChannel01 = "Bruno e Marrone"
    nameChannel02 = "Gustavo Lima"
    # path do diretorio que contem os dados do canal 1
    pathChannel01 = "C:\\TCC\\Network\\ColetaRedeComplexa_CSV\\Bruno e Marrone"
    # path do diretorio que contem os dados do canal 2
    pathChannel02 = "C:\\TCC\\Network\\ColetaRedeComplexa_CSV\\Gustavo Lima"

    # montar as redes
    graphsChannel01 = montar_rede_strong(pathChannel01, nameChannel01)
    graphsChannel02 = montar_rede_strong(pathChannel02, nameChannel02)

    # calculando as metricas para cada componente do grafo 1
    metricasComponentes01 = calcular_metricas_componentes2(graphsChannel01)

    # calculando as metricas para cada componente do grafo 2
    metricasComponentes02 = calcular_metricas_componentes2(graphsChannel02)
    
    components01 = [nx.strongly_connected_components(graph) for graph in graphsChannel01]
    metricas_globais01 = calcular_metricas_globais(graphsChannel01, components01)

    components02 = [nx.strongly_connected_components(graph) for graph in graphsChannel02]
    # Calcular as metricas de cada componente separadamente e juntar em um dicionario de metricas globais
    metricas_globais02 = calcular_metricas_globais(graphsChannel02, components02)

    # salvando as metricas em um arquivo csv
    save_metrics_to_csv(metricas_globais01, metricasComponentes01, metricas_globais02, metricasComponentes02, 'metricas.csv')

main()