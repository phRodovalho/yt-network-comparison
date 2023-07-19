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
    config.read("C:\\Users\\pheli\\Desktop\\Comparar redes complexas\\yt-network-comparison\\Coleta\\config.ini")
    return config


def main():
    # carregando configurações do arquivo config.ini
    config = load_config()

    # criando objeto youtube
    youtube = Youtube(config['settings']['developer_key'])

    # variaveis com os canais iniciais
    networkChannelsName = config['network_channels_name']
    networkChannelsLink = config['network_channels_link']

    # lista das listas com os canais iniciais
    listChannels = list(zip(networkChannelsName.values(),
                            networkChannelsLink.values()))
    
    # convert tuple to list
    listChannels = [list(elem) for elem in listChannels]

    depth = int(config['settings']['depth'])

    # criando as redes complexas de cada um dos canais iniciais
    for channel in listChannels:
        # confirmando profundidade de busca para a rede de cada canal
        print("Profundidade de busca " + str(depth) +
              " para o canal " + channel[0])
        # criando a rede complexa
        collectData(youtube, channel, depth)


def collectData(youtube, channel, depth):
    # extraindo id do canal a partir do link
    channel[1] = channel[1].split('/')[-1]
    # criando primeira lista com o canal inicial e os seus canais de subscrições
    networkLevel = getChannelSubscriptionInfo(youtube, [channel])
    networkLevel['Level'] = 1

    for i in range(1, depth):
        # extraindo novos canais a partir da lista anterior
        IdChannells = extractNewSourceTarget(networkLevel, i)
        # criando lista com os canais de subscription dos canais da lista anterior
        networkLevelN = getChannelSubscriptionInfo(
            youtube, IdChannells.values.tolist())
        networkLevelN['Level'] = i + 1
        # concatenando as listas anteriores
        networkLevel = pd.concat([networkLevel, networkLevelN])

    # criando CSV com os dados da rede
    exportNetworkToCSV(networkLevel, channel[0])


def getChannelSubscriptionInfo(youtube, channelInfos):
    '''
    Documentação da API na pagina de subscriptions
    https://developers.google.com/youtube/v3/docs/subscriptions
    '''

    # criando dataframe para armazenar os dados
    network = pd.DataFrame({
        'Source': [],
        'Target': [],
        'SourceId': [],
        'TargetId': [],
        'TargetDescription': [],
        'TargetPublishedAt': []
    })

    # percorrendo a lista de canais
    for i in range(len(channelInfos)):
        next = True
        nextPageToken = ""
        while next:
            channelSubs = [{}]

            # chamando a função que retorna os dados da API
            request = youtube.youtube.subscriptions().list(
                part="contentDetails,id,snippet,subscriberSnippet",
                channelId=channelInfos[i][1],
                pageToken=nextPageToken,
                mySubscribers=True,
                maxResults=50
            )
            # executando a requisição
            try:
                response = request.execute()
            except:
                # caso o canal não habilite a visualização de sua lista de subscrições
                print("Erro ao executar a requisição")
                print(f"O canal {channelInfos[i][0]} não permite visualizar a lista de inscricoes")
                break

            # percorrendo a lista de items
            for j, subscription in enumerate(response['items']):
                # extraindo os dados relevantes do canal
                if 'snippet' in subscription:
                    snippet = subscription['snippet']
                    channelTitle = snippet['title']  # nome do canal
                    # id do canal
                    channelSubId = snippet['resourceId']['channelId']
                    
                    # salvando descricao do canal
                    if 'description' in snippet:
                        description = snippet['description']
                    else: # caso não exista descrição
                        description = ""
                    
                    # salvando data de inscrição
                    publishedAt = snippet['publishedAt']
                    publishedAt = publishedAt.split('T')[0]

                    # associando o canal atual com o canal que ele está inscrito
                    channelSubs.append({'Source': channelInfos[i][0], 'Target': channelTitle,
                                        'SourceId': channelInfos[i][1], 'TargetId': channelSubId,
                                        'TargetDescription': description, 'TargetPublishedAt': publishedAt})

            # inserindo os dados extraidos na lista de redes dos canais
            network = pd.concat([network, pd.DataFrame(channelSubs)])

            # verificando se existe uma próxima página
            if 'nextPageToken' in response:
                next = True
                nextPageToken = response['nextPageToken']
            else:
                # caso não exista uma próxima página, a variável next é alterada para False
                next = False
                nextPageToken = ''

    # removendo as linhas vazias provenientes da primeira linha da lista channelSubs
    network = network.dropna()
    return network

def extractNewSourceTarget(listIni, level):
    # copy only rown where level is equal to level
    listLevel = listIni[listIni['Level'] == level].copy()
    df = listLevel[['Target', 'TargetId']].copy()
    # rename columns
    df.columns = ['Source', 'SourceId']
    return df

def exportNetworkToCSV(network, nameChannel):
    # criando diretorio com o nome do canal de origem
    path = createDir(pathchannelDir + "\\" + nameChannel)
    # Criando CSV de NOS
    # criando dataframe com os nos
    nos = criaDataFrameNos(network)
    # exportando para csv
    nos.to_csv(path + "\\Nos.csv", index=False)

    # Criando CSV de ARESTAS
    # criando dataframe com as arestas
    arestas = criaDataFrameArestas(network)
    # exportando para CSV
    arestas.to_csv(path + "\\Arestas.csv", index=False)
    network.to_csv(path + '\\TotalNetwork.csv', index=False)

def createDir(nameDir):
    path = os.path.join(nameDir)
    try:
        os.mkdir(path)
        return path
    except OSError as error:
        print(error)
        return path

def criaDataFrameNos(network):
    # criando outro dataframe a partir do atual selecionando as colunas
    nos = network[['Source', 'SourceId']].copy()
    # renomeando as colunas
    nos.columns = ['Id', 'Label']
    # removendo duplicados'
    nos = nos.drop_duplicates()

    # criando outro dataframe a partir do atual selecionando as colunas
    nos2 = network[['Target', 'TargetId']].copy()
    # renomeando as colunas
    nos2.columns = ['Label', 'Id']
    # removendo duplicados'
    nos2 = nos2.drop_duplicates()

    # concatenando os dois dataframes
    nos = pd.concat([nos, nos2])
    # removendo duplicados
    nos = nos.drop_duplicates()
    # ordenando o dataframe
    nos = nos.sort_values(by=['Label'])
    return nos

def criaDataFrameArestas(network):
    # criando outro dataframe a partir do atual com todas as colunas
    arestas = network.copy()
    # renomeando as colunas
    arestas.columns = ['NomeCanalSeguidor', 'NomeCanalSeguido', 'Source', 'Target', 'Descricao', 'DataPublicacao','Profundidade']
    # removendo duplicados'
    # arestas = arestas.drop_duplicates()
    # adicionando coluna Type com valor "Directed"
    arestas['Type'] = 'Directed'
    # ordenando o dataframe
    arestas = arestas.sort_values(by=['NomeCanalSeguidor'])

    return arestas

pathchannelDir = createDir("ColetaDeDados")

main()
