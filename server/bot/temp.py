

import pandas as pd

one = pd.read_csv("bitcoin.csv")
two = pd.read_csv("bitcoin2.csv")
two = two[::-1]
two['Volume'] = [float(v[:-1])*1000 for v in two['Volume']]

df = pd.concat([one, two])

df = df.drop('Currency', axis=1)
df = df.drop('Change', axis=1)
print(one)
print(two)
print(df)

df.to_csv("bitcoin_total.csv", index=False)