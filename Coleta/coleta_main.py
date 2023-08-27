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
import datetime
def load_config():
    config = configparser.ConfigParser()
    config.read("C:\\Users\\pheli\\Desktop\\Comparar redes complexas\\yt-network-comparison\\Coleta\\config.ini")
    return config

# TODO COLETA: contar quantidade de pessoas seguidas e as que não permitem visualizar
# TODO COLETA: comparar redes de pessoas publicas e pessoas comuns

def main():
    config = load_config()

    youtube = Youtube(config['settings']['developer_key'])
    depth = int(config['settings']['depth'])

    for channel_name, channel_link in config['channels'].items():
        network_data = collect_channel_data(youtube, [channel_name, channel_link], depth)
        exportNetworkToCSV(network_data, channel_name)

# TODO COLETA: contar quantidade de pessoas seguidas e as que não permitem visualizar
# TODO COLETA: comparar redes de pessoas publicas e pessoas comuns

def collect_channel_data(youtube, channel, depth):
    idChannel = channel[1].split('/')[-1]
    nameChannel = channel[0]

    networkLevel = get_channel_subscription_info(youtube, nameChannel, idChannel)
    networkLevel['Level'] = 1

    for i in range(1, depth):
        IdChannells = extractNewSourceTarget(networkLevel, i)
        for _, row in IdChannells.iterrows():
            networkLevelN = get_channel_subscription_info(youtube, row['Source'], row['SourceId'])
            networkLevelN['Level'] = i + 1
            networkLevel = pd.concat([networkLevel, networkLevelN])

    return networkLevel


def get_channel_subscription_info(youtube, nameChannel, idChannel):
    '''
    Documentação da API na pagina de subscriptions
    https://developers.google.com/youtube/v3/docs/subscriptions
    '''
    next = True
    nextPageToken = ""
    countError = 0
    countSucess = 0
    channelData = []
    
    while next:
        request = youtube.youtube.subscriptions().list(
            part="contentDetails,id,snippet,subscriberSnippet",
            channelId=idChannel,
            pageToken=nextPageToken,
            maxResults=50
        )
        try:
            response = request.execute()
        except Exception as e:
            print("Erro ao executar a requisição")
            print(e.reason) 
            print(f"O canal {nameChannel} não permite visualizar a lista de inscricoes")
            channelData.append({'Source': nameChannel, 'Target': "subscriptionForbidden",
                                    'SourceId': idChannel, 'TargetId': "subscriptionForbidden",
                                    'SourceDescription': "", 'TargetDescription': e.reason, 
                                    'TargetPublishedAt': ""})
            countError += 1
            break

        if 'nextPageToken' in response:
            next = True
            nextPageToken = response['nextPageToken']
        else:
            next = False
            nextPageToken = ''

        for j, subscription in enumerate(response['items']):
            # dados do canal seguido (subscription)
            if 'snippet' in subscription:
                snippet = subscription['snippet']
                subscriptionChannelName = snippet['title']
                subscriptionChannelId = snippet['resourceId']['channelId']
                
                if 'description' in snippet:
                    subscriptionDescription = snippet['description']
                else:
                    subscriptionDescription = ""
                
                subscriptionPublishedAt = snippet['publishedAt'].split('T')[0]
            else:
                print("Erro ao executar a requisição")
                print(f"O canal {nameChannel} não permite visualizar a lista de inscricoes")
                countError += 1
                break
            
            # dados do canal seguidor (subscriber)
            if 'subscriberSnippet' in subscription:
                subscriberSnippet = subscription['subscriberSnippet']
                subscriberChannelId = subscriberSnippet['channelId']
                subscriberChannelName = subscriberSnippet['title']
                subscriberDescription = subscriberSnippet['description']

            # associando o canal seguidor com o canal que ele está seguindo
            channelData.append({'Source': subscriberChannelName, 'Target': subscriptionChannelName,
                                    'SourceId': subscriberChannelId, 'TargetId': subscriptionChannelId,
                                    'SourceDescription': subscriberDescription, 'TargetDescription': subscriptionDescription, 
                                    'TargetPublishedAt': subscriptionPublishedAt})
            countSucess += 1
            
    channelDataFrame = pd.DataFrame(channelData)
    return channelDataFrame

def extractNewSourceTarget(listIni, level):
    listLevel = listIni[listIni['Level'] == level].copy()
    df = listLevel[['Target', 'TargetId']].copy()
    df.columns = ['Source', 'SourceId']
    return df

def exportNetworkToCSV(network, nameChannel):
    formatted_time = datetime.datetime.now().strftime("%d_%m_%Y_%Hh%Mm")
    path = createDir(pathchannelDir + "\\" + nameChannel + "_" + formatted_time)

    nos = criaDataFrameNos(network)
    arestas = criaDataFrameArestas(network)

    nos.to_csv(path + "\\Nos.csv", index=False)
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
    nos = network[['Source', 'SourceId']].copy()
    nos.columns = ['Label', 'Id']

    nos2 = network[['Target', 'TargetId']].copy()
    nos2.columns = ['Label', 'Id']

    nos = pd.concat([nos, nos2])
    nos = nos.drop_duplicates()
    return nos

def criaDataFrameArestas(network):
    arestas = network.copy()
    arestas.columns = ['NomeCanalSeguidor', 'NomeCanalSeguido', 'Source', 'Target', 'SourceDescricao', 'TargetDescricao', 'DataPublicacao','Profundidade']
    arestas['Type'] = 'Directed'
    return arestas

pathchannelDir = createDir("ColetaDeDados")

main()
