

# use the backdata (5y) to find average daily move

import pandas as pd
import math

data = pd.read_csv("spx_hist.csv")#[:249]
data["percent_change"] = (data['Close'] - data['Open']) / data['Open'] *100

# trades = []
# nc = 7
# extra = 0
# for i, pc in enumerate(data['percent_change']):
#   trades.append((40 if pc < 1 else -100) *nc)
#   extra += trades[-1]
  # if nc < 8 and extra > 455:
  #   nc += 1
  #   extra -= 455
    # nc += math.floor(extra / 455)
    # extra -= math.floor(extra / 455)
# print(f"{trades} trades; max contracts {nc}")
# print(f"Return: ${sum(trades)}")


# print(data["percent_change"])
# data["dollar_change"] = (data['Close'] - data['Open'])
# print(data["dollar_change"])
# print(data["dollar_change"].mean())


# print(data.var())

# mT = len(data.loc[data['percent_change'].abs() >= 5])
# l5T = len(data.loc[data['percent_change'].abs() < 5])
# l4T = len(data.loc[data['percent_change'].abs() < 4])
# l3T = len(data.loc[data['percent_change'].abs() < 3])
# l2T = len(data.loc[data['percent_change'].abs() < 2])
# l1T = len(data.loc[data['percent_change'].abs() < 1])
# l05T = len(data.loc[data['percent_change'].abs() < 0.5])
# l33T = len(data.loc[data['percent_change'].abs() < 0.33])
# T33l = len(data.loc[data['percent_change'].abs() > 0.33])

gold = data[data['percent_change'].abs() <= 1]
gold = gold[gold['percent_change'].abs() >= 0.33]

# print(f"More than 5% - {mT}  ({mT/len(data)*100}% of the time)")
# print(f"Less than 5% - {l5T}  ({l5T/len(data)*100}% of the time)")
# print(f"Less than 4% - {l4T}  ({l4T/len(data)*100}% of the time)")
# print(f"Less than 3% - {l3T}  ({l3T/len(data)*100}% of the time)")
# print(f"Less than 2% - {l2T}  ({l2T/len(data)*100}% of the time)")
# print(f"Less than 1% - {l1T}  ({l1T/len(data)*100}% of the time)")
# print(f"Less than 0.5% - {l05T}  ({l05T/len(data)*100}% of the time)")
# print(f"Less than 0.33% - {l33T}  ({l33T/len(data)*100}% of the time)")
print(f"More than 0.33% but less than 1% - {len(gold)}  ({len(gold)/len(data)*100}% of the time)")

# mT = len(data.loc[data['dollar_change'].abs() >= 100])
# l5T = len(data.loc[data['dollar_change'].abs() < 80])
# l4T = len(data.loc[data['dollar_change'].abs() < 50])
# l3T = len(data.loc[data['dollar_change'].abs() < 10])
# l2T = len(data.loc[data['dollar_change'].abs() < 5])
# l1T = len(data.loc[data['dollar_change'].abs() < 1])
# l05T = len(data.loc[data['dollar_change'].abs() < 0.5])

# print(f"More than $100 - {mT}  ({mT/len(data)*100}% of the time)")
# print(f"Less than $100 - {l5T}  ({l5T/len(data)*100}% of the time)")
# print(f"Less than $50 - {l4T}  ({l4T/len(data)*100}% of the time)")
# print(f"Less than $10 - {l3T}  ({l3T/len(data)*100}% of the time)")
# print(f"Less than $5 - {l2T}  ({l2T/len(data)*100}% of the time)")
# print(f"Less than $1 - {l1T}  ({l1T/len(data)*100}% of the time)")
# print(f"Less than $0.5 - {l05T}  ({l05T/len(data)*100}% of the time)")


"""
More than 5% - 5  (0.33178500331785005% of the time)
Less than 5% - 1502  (99.66821499668215% of the time)
Less than 4% - 1495  (99.20371599203716% of the time)
Less than 3% - 1485  (98.54014598540147% of the time)
Less than 2% - 1436  (95.28865295288654% of the time)
Less than 1% - 1189  (78.89847378898473% of the time)
Less than 0.5% - 741  (49.170537491705375% of the time)
"""

"""
              Open         High          Low        Close    Adj Close  percent_change  dollar_change
count  1507.000000  1507.000000  1507.000000  1507.000000  1507.000000     1507.000000    1507.000000
mean   4581.720292  4608.168261  4553.410312  4582.585547  4582.585547        0.023523       0.865255
std    1026.604886  1026.606311  1026.148997  1026.673194  1026.673194        1.003411      41.922701
min    2290.710000  2300.730000  2191.860000  2237.400000  2237.400000       -5.709920    -218.060000
25%    3909.960000  3930.955000  3876.935000  3907.450000  3907.450000       -0.431059     -19.765000
50%    4380.940000  4410.310000  4356.290000  4380.260000  4380.260000        0.050521       2.470000
75%    5347.845000  5373.140000  5313.385000  5353.495000  5353.495000        0.566792      25.570000
max    6936.020000  6945.770000  6921.600000  6932.050000  6932.050000        9.901154     491.620000
"""

"""
  print(data.var())
Open              1.053918e+06
High              1.053921e+06
Low               1.052982e+06
Close             1.054058e+06
Adj Close         1.054058e+06
percent_change    1.006833e+00
"""