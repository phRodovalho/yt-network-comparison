"""
Coleta de dados de dois canais do Youtube
Estruturado para a partir de um canal inicial coletar os canais de subscription
e a partir desses canais coletar os canais de subscription e assim por diante
até atingir a profundidade de busca definida pelo usuário.

Após a coleta de dados será criado um dataframe com os dados coletados e
será exportado para um arquivo .CSV para ser usado no Gephi, em seguida será
criado a partir do dataframe a rede complexa feita com os dados coletados.

Para executar corretamente:
No terminal digite o comando abaixo para instalar as bibliotecas necessárias
pip install -r requirements.txt

Ao chamar defina os dois canais iniciais e a profundidade de busca no arquivo
de configuração config.ini
"""

import os
import pandas as pd 
import configparser
from IPython.display import display
from functionsYT import Youtube

# Carrega as configurações do arquivo config.ini
def load_config():
    config = configparser.ConfigParser()
    config.read("C:\\TCC\\Network\\Network\\config.ini")
    return config



