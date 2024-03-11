import pandas as pd

# Läs in CSV-filen till en DataFrame
df = pd.read_csv('SMHI_python3.csv',  delimiter=";", decimal=",")
df_med = pd.read_csv('SMHI_python_medel.csv', delimiter=";", decimal=",")
#df = df.iloc[:, :-6]
#df.insert(0, 'ID', range(len(df)))
# Convert all values to numeric type
print(df)
# Visa de första raderna av DataFrame för att verifiera att filen har lästs in korrekt
print(df.head())
print(df_med.head())
# Assuming 'df' is your modified DataFrame
df.to_csv('SMHI_modified3.csv', index=False)
df_med.to_csv('SMHI_modified_medel.csv', index=False)