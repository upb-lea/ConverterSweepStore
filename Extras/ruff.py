import pandas as pd
import random
#Generate 5 random numbers between 10 and 30


#object = pd.read_csv(r'calc\Thermal\DatasheetDB.csv')
#total_rows = len(object)
#print(object)
#randomlist = random.sample(range(10, 200), total_rows)
#object['D1'] = randomlist
#object.to_pickle(r'calc_AFE\results.pkl')

df = pd.read_pickle(r'calc\results.pk')
newdf = df[~df['V_DC'].isin([185,200,215,350,320])]
newdf.to_pickle(r'calc\resultsnew.pk')
#readdf = pd.read_pickle('resultsnew.pk')
#show(readdf)