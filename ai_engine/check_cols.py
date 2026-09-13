import pandas as pd
csv_path = r"d:\programs\sih_isro\IO-VNBD\Synchronised V abd S datasets\Categorised IOVNB Dataset\M (Driver B)\S-M.csv"
df = pd.read_csv(csv_path, encoding='latin1', nrows=1)
cols = df.columns.str.strip().tolist()
print("Columns:")
for c in cols:
    print(repr(c))
