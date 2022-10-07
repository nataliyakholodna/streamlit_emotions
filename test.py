import pandas as pd

df = pd.read_csv('data/2021-05-02.csv')
df.date = df.date.todatetime()