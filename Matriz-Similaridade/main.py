import pandas as pd
from sklearn.metrics import pairwise_distances
import seaborn as sns
import matplotlib.pyplot as plt

dados = {
    'Canal': ['stationdaniela', 'mister_beep', 'henriquemares', 'rosanelicar', 'tvserradouradasbt', 'bandjornalismo', 'leonardo', 'tecmundo', 'melim', 'gustavolima', 'gloriagroove', 'pabllovitar', 'zeramalho'],
    'stationdaniela': [1.0, 0.97716001, 0.97708827, 0.98919347, 0.88748326, 0.99359625, 0.99999167, 0.93900067, 0.96302025, 0.9995194, 0.92415707, 0.95288236, 0.99613347],
    'mister_beep': [0.97716001, 1.0, 0.99999994, 0.93544398, 0.7715741, 0.994913, 0.97629091, 0.99063758, 0.88377032, 0.98327707, 0.98422889, 0.99557978, 0.99205093],
    'henriquemares': [0.97708827, 0.99999994, 1.0, 0.93532478, 0.77137151, 0.99487901, 0.9762179, 0.99068356, 0.88361256, 0.98321564, 0.98428849, 0.99561139, 0.99200842],
    'rosanelicar': [0.98919347, 0.93544398, 0.93532478, 1.0, 0.94392298, 0.96629355, 0.98977956, 0.87843032, 0.99211595, 0.984174, 0.8581615, 0.89811091, 0.97248819],
    'tvserradouradasbt': [0.88748326, 0.7715741, 0.77137151, 0.94392298, 1.0, 0.8309755, 0.88933452, 0.6785665, 0.97597821, 0.8731345, 0.64824729, 0.7091459, 0.84450967],
    'bandjornalismo': [0.99359625, 0.994913, 0.99487901, 0.96629355, 0.8309755, 1.0, 0.99313044, 0.97184581, 0.9264118, 0.99662108, 0.96140181, 0.98105409, 0.99968076],
    'leonardo': [0.99999167, 0.97629091, 0.9762179, 0.98977956, 0.88933452, 0.99313044, 1.0, 0.93759949, 0.96410429, 0.99938574, 0.92260167, 0.95164545, 0.99576922],
    'tecmundo': [0.93900067, 0.99063758, 0.99068356, 0.87843032, 0.6785665, 0.97184581, 0.93759949, 1.0, 0.81161659, 0.9492092, 0.99916413, 0.99908047, 0.96558391],
    'melim': [0.96302025, 0.88377032, 0.88361256, 0.99211595, 0.97597821, 0.9264118, 0.96410429, 0.81161659, 1.0, 0.95420692, 0.78705743, 0.83591698, 0.93562674],
    'gustavolima': [0.9995194, 0.98327707, 0.98321564, 0.984174, 0.8731345, 0.99662108, 0.99938574, 0.9492092, 0.95420692, 1.0, 0.93555358, 0.96182656, 0.99837774],
    'gloriagroove': [0.92415707, 0.98422889, 0.98428849, 0.8581615, 0.64824729, 0.96140181, 0.92260167, 0.99916413, 0.78705743, 0.93555358, 1.0, 0.99649274, 0.95414467],
    'pabllovitar': [0.95288236, 0.99557978, 0.99561139, 0.89811091, 0.7091459, 0.98105409, 0.95164545, 0.99908047, 0.83591698, 0.96182656, 0.99649274, 1.0, 0.97584729],
    'zeramalho': [0.99613347, 0.99205093, 0.99200842, 0.97248819, 0.84450967, 0.99968076, 0.99576922, 0.96558391, 0.93562674, 0.99837774, 0.95414467, 0.97584729, 1.0]
}

df = pd.DataFrame(dados)
df.set_index('Canal', inplace=True)

similaridade_pearson = 1 - pairwise_distances(df, metric='correlation')

plt.figure(figsize=(10, 8))
sns.set(font_scale=1)
sns.heatmap(similaridade_pearson, annot=True, cmap='YlGnBu', xticklabels=dados['Canal'], yticklabels=dados['Canal'])
plt.title('Matriz de Similaridade de Pearson')
plt.show()


