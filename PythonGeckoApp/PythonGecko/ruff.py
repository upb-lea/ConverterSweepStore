import pandas as pd
import random
#Generate 5 random numbers between 10 and 30


object = pd.read_pickle(r'calc\results.pk')
total_rows = len(object)

#randomlist = random.sample(range(10, 200), total_rows)
#object['D1'] = randomlist
#object.to_pickle(r'calc_AFE\results.pkl')
