import networkx as nx
import pandas as pd
from pyvis.network import Network
import scipy.stats as stats
from tkinter import *
import os
import numpy as np
import json

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

    # convert int32 to int
    edgesList['Profundidade'] = edgesList['Profundidade'].astype('int64').apply(lambda x: int(x))
    # adicionando as arestas na rede
    edge_attrs = {
        'NomeCanalSeguidor': edgesList['NomeCanalSeguidor'],
        'NomeCanalSeguido': edgesList['NomeCanalSeguido'],
        'Descricao': edgesList['Descricao'],
        'DataPublicacao': edgesList['DataPublicacao'],
        'Profundidade': edgesList['Profundidade'],
        'Type': edgesList['Type']
    }

    edges = [(row['Source'], row['Target'], {k: attrs[i] for k, attrs in edge_attrs.items()}) for i, row in edgesList.iterrows()]
    graph.add_edges_from(edges)

    return graph


def drawing_network(graph):
    # Draw the network using Pyvis
    net = Network(notebook=False, height="100%", width="100%")
    net.from_nx(graph)
    net.show_buttons(filter_=['nodes', 'edges', 'physics', 'layout', 'interaction', 'selection'])
    net.force_atlas_2based()

    return net

def export_network(net, name, path):
    pathFile = path + "\\rede" + name + ".html"

    try:
        # net.show(pathFile)
        # Export the network in HTML
        export_html = json.dumps(net.get_graph())
        with open(pathFile, 'w+') as f:
            f.write(export_html)
        return True
    except Exception as e:
        print(e)
        print("Erro ao gerar a rede do canal: " + name)
        return False
    
def export_network_gexf(graph, name, path):
    # Exporta a rede em formato GEXF
    pathFile = os.path.join(path, f"rede_{name}.gexf")
    nx.write_gexf(graph, pathFile)

    # Retorna True para indicar que a exportação foi bem-sucedida
    return True

def export_network_html(net, name, path):
    pathFile = os.path.join(path, f"rede_{name}.html")

    try:
        net.save_graph(pathFile)
        return True
    except Exception as e:
        print(e)
        print("Erro ao gerar a rede do canal: " + name)
        return False


def main():
    # Montagem da rede dos canais a partir dos dados coletados
    channels = ["ColetaDeDados\\Gustavo Lima", "ColetaDeDados\\Leonardo"]

    for pathChannel in channels:
        name = pathChannel.split("\\")[1]
        graph = montar_rede(pathChannel, name)
        network = drawing_network(graph)
        export_network(network, name, pathChannel)
        export_network_html(network, name, pathChannel)
        export_network_gexf(graph, name, pathChannel)


main()