import pandas as pd


f1, f2 = 'linhas_astransp.txt', 'linhas_bus2.txt'

c1=pd.read_csv(f1, header=None)
c2=pd.read_csv(f2, header=None)

for i1 in list(c1.values.ravel()):
    if i1 not in list(c2.values.ravel()):
        print(i1)