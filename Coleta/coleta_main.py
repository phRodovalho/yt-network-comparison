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
import time
import datetime
import pandas as pd 
import configparser
from functionsYT import Youtube

timeFile = datetime.datetime.now().strftime("%d.%m_%Hh")
output_file_path = os.path.join(os.getcwd(), "log_execucao_coleta_ytApi_"+ timeFile +"_.txt")

def load_config():
    config = configparser.ConfigParser()
    config.read("C:\\Users\\pheli\\Desktop\\Comparar redes complexas\\yt-network-comparison\\Coleta\\config.ini")
    return config

def createDir(nameDir):
    path = os.path.join(nameDir)
    try:
        os.mkdir(path)
        return path
    except OSError as error:
        print(error)
        return path

def save_file(msg):
    with open(output_file_path, "a", encoding="utf-8") as output_file:
        output_file.write(msg + "\n")

def get_end_time(start_time):
    end_time = time.time()
    elapsed_time = (end_time - start_time)/60
    return round(elapsed_time, 2)

def collect_channel_data(youtube, channel, depth):
    idChannel = channel[1].split('/')[-1]
    nameChannel = channel[0]

    networkLevel = get_channel_subscription_info(youtube, nameChannel, idChannel, 1)
    save_file(f"\n---- Finalizado a coleta!, Iniciando coleta dos canais que o {nameChannel} segue! ---- ")

    for i in range(1, depth):
        IdChannells = extractNewSourceTarget(networkLevel, i)
        for numCanais, row in IdChannells.iterrows():
            save_file(f"\n---- Iniciando coleta do canal {row['Source']}, nivel {i + 1} ---- ")
            start_time_collectChannel = time.time()
            networkLevelN = get_channel_subscription_info(youtube, row['Source'], row['SourceId'], i + 1)
            networkLevel = pd.concat([networkLevel, networkLevelN])
            save_file(f"\n---- Coleta finalizada! ---- ")

        save_file(f"\n---- Coleta de nivel {i+1} finalizada em {get_end_time(start_time_collectChannel)} minutos ---- ")
        save_file(f"\n---- Quantidade de canais analisados = {qntCanaisAnalisados} ---- ")
        save_file(f"\n---- Quantidade de canais não analisados = {qntCanaisNaoAnalisados} ---- ")
        save_file(f"\n Porcentagem de coleta do nivel {i+1} = {round((qntCanaisAnalisados/(qntCanaisAnalisados + qntCanaisNaoAnalisados))*100, 2)}% ")

    return networkLevel

def get_channel_subscription_info(youtube, nameChannel, idChannel, level):
    '''
    Documentação da API na pagina de subscriptions
    https://developers.google.com/youtube/v3/docs/subscriptions
    '''
    next = True
    nextPageToken = ""
    channelData = []
    channelData = []
    global qntCanaisNaoAnalisados
    global countSucess
    global qntCanaisAnalisados
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
            if(e.reason != "The requester is not allowed to access the requested subscriptions."):
                save_file(f"\n---- Erro ao executar a requisição ---- ")
                save_file(f"\nDetalhes do erro: {e.reason} ")
            else:
                channelData.append({'Source': nameChannel, 'Target': "subscriptionForbidden",
                                    'SourceId': idChannel, 'TargetId': "subscriptionForbidden",
                                    'TargetDescription': e.reason, 'TargetPublishedAt': "", 'Level': level})
                save_file(f"\n---- Erro ao executar a requisição ---- ")
                save_file(f"\nCanal {nameChannel} não permite visualizar a lista de inscricoes ")
                qntCanaisNaoAnalisados += 1
            break

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
                qntCanaisNaoAnalisados += 1
                break
            
            # dados do canal seguidor (subscriber)
            if 'subscriberSnippet' in subscription:
                subscriberSnippet = subscription['subscriberSnippet']
                subscriberChannelName = subscriberSnippet['title']
                subscriberChannelId = subscriberSnippet['channelId']
                subscriberDescription = subscriberSnippet['description']

            # associando o canal seguidor com o canal que ele está seguindo
            channelData.append({'Source': subscriberChannelName, 'Target': subscriptionChannelName,
                                    'SourceId': subscriberChannelId, 'TargetId': subscriptionChannelId,
                                    'TargetDescription': subscriptionDescription, 'TargetPublishedAt': subscriptionPublishedAt,
                                    'Level': level})
            countSucess += 1

        if 'nextPageToken' in response:
            next = True
            nextPageToken = response['nextPageToken']
        else:
            next = False
            nextPageToken = ''
            save_file(f"\n O canal {nameChannel} segue {response['pageInfo']['totalResults']} canais ")
            qntCanaisAnalisados += response['pageInfo']['totalResults']

    if level == 1: # adiciona o canal inicial como um nó da rede
        channelData.append({'Source': subscriberChannelName, 'Target': subscriberChannelName,
                                        'SourceId': subscriberChannelId, 'TargetId': subscriberChannelId,
                                        'TargetDescription': subscriberDescription, 'TargetPublishedAt': "",
                                        'Level': 0})

    channelDataFrame = pd.DataFrame(channelData)
    return channelDataFrame

def extractNewSourceTarget(dataframe, level):
    level_filtered = dataframe[dataframe['Level'] == level].copy()
    valid_targets = level_filtered[level_filtered['TargetId'] != "subscriptionForbidden"].copy()
    extracted_data = valid_targets[['Target', 'TargetId']].copy()
    extracted_data.columns = ['Source', 'SourceId']
    return extracted_data

def exportNetworkToCSV(network, nameChannel):
    formatted_time = datetime.datetime.now().strftime("%d_%m_%Y_%Hh%Mm")
    path = createDir(pathchannelDir + "\\" + nameChannel + "_" + formatted_time)

    network.drop_duplicates()
    nos = criaDataFrameNos(network)
    arestas = criaDataFrameArestas(network)

    nos.to_csv(path + "\\Nos.csv", index=False)
    arestas.to_csv(path + "\\Arestas.csv", index=False)
    network.to_csv(path + '\\TotalNetwork.csv', index=False)

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
    arestas.columns = ['NomeCanalSeguidor', 'NomeCanalSeguido', 'Source', 'Target', 'TargetDescricao', 'DataPublicacao','Profundidade']
    arestas['Type'] = 'Directed'
    return arestas

# TODO COLETA: comparar redes de pessoas publicas e pessoas comuns

qntCanaisAnalisados = 0
countSucess = 0
qntCanaisNaoAnalisados = 0

def main():
    start_time_programa = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    init_time_program = time.time()
    save_file(f"\n---- Iniciando Programa em {start_time_programa} ---- ")
    
    
    config = load_config()
    youtube = Youtube(config['settings']['developer_key'])
    depth = int(config['settings']['depth'])

    for channel_name, channel_link in config['channels'].items():
        save_file(f"\n---- Iniciando coleta do canal {channel_name}, nivel 1 ---- ")
        start_time_collectChannel = time.time()
        network_data = collect_channel_data(youtube, [channel_name, channel_link], depth)
        save_file(f"\n---- Canal {channel_name} coletado em 3 niveis, em {get_end_time(start_time_collectChannel)} minutos ---- ")
        save_file(f"\n---- Exportando canal {channel_name} em CSV ---- ")
        exportNetworkToCSV(network_data, channel_name)

    save_file(f"\n---- Fim do Programa! Execução levou {get_end_time(init_time_program)} minutos ---- ")

pathchannelDir = createDir("ColetaDeDados")

if __name__ == "__main__":
    main()
