import pandas as pd

df = pd.read_csv("data/cleaned_anzhfr_full.csv")
count = df[df["n_imputed_fields"] >= 0].shape[0]
print(count)
# Age, Gender, Fracture Type, Surgery Type, Hospital Code