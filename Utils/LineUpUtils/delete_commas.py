import pandas as pd

# Line 587 index 585 is for some reason all commas
csv = r"C:\Users\nitro\WhoCaresAboutHUDandPitchComms\csv\NewHeightMetrics(ZoneDim).csv"
df = pd.read_csv(csv)
df = df.drop(df.index[585])

df.to_csv(csv, index=False)