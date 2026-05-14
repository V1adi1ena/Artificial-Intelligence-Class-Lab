import pandas as pd

columns = [f"A{i}" for i in range(1, 25)]
columns.append("target")

df = pd.read_csv(
    "german.data-numeric",
    sep=r"\s+",
    header=None,
    names=columns
)

print(df.head())

