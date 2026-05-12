import pandas as pd
import numpy as np

print("Démarrage de la grande fusion (Correction des Dates)...")

# Fonction pour les métriques
def nettoyer_metriques(val):
    val = str(val).lower().strip().replace(';;;', '')
    if val in ['nan', 'none', '', 'null']: return 0
    if 'k' in val: return int(float(val.replace('k', '')) * 1000)
    if 'm' in val: return int(float(val.replace('m', '')) * 1000000)
    try: return int(float(val))
    except: return 0

# --- 1. ARCHIVE TWITTER (2009-2021) ---
print("1/4 - Twitter...")
df1 = pd.read_csv('2009-2021.csv', low_memory=False)
df1 = df1[df1['isRetweet'] == 'f']
df1 = df1.rename(columns={'favorites': 'likes', 'retweets': 'shares'})
df1 = df1[['id', 'date', 'text', 'likes', 'shares']]
# Conversion de date spécifique (Format Standard)
df1['date'] = pd.to_datetime(df1['date'], utc=True, errors='coerce')


# --- 2. ARCHIVE TRUTH SOCIAL (2022-2025) ---
print("2/4 - Truth Social...")
df2 = pd.read_csv('2022-02-14 to 2025-10-25.csv', low_memory=False)
df2 = df2.dropna(subset=['content'])
df2 = df2[~df2['content'].str.startswith('RT @')]
df2 = df2.rename(columns={
    'created_at': 'date', 
    'content': 'text', 
    'favourites_count': 'likes', 
    'reblogs_count': 'shares'
})
df2 = df2[['id', 'date', 'text', 'likes', 'shares']]
# Conversion de date spécifique (Format ISO 8601 avec T et Z)
df2['date'] = pd.to_datetime(df2['date'], utc=True, errors='coerce')


# --- 3. SCRAPING SELENIUM (Fin 2025-Mars 2026) ---
print("3/4 - Selenium...")
df3 = pd.read_csv('trump_data_oct25_mar26_COMPLET_02h50m58s.csv')
df3 = df3[['id', 'date', 'text', 'likes', 'shares']]
# Conversion de date spécifique (Format Américain Ex: "Mar 25, 2026, 4:24 PM")
# On utilise format='mixed' pour dire à Pandas de se débrouiller avec les textes complexes
df3['date'] = pd.to_datetime(df3['date'], format='mixed', utc=True, errors='coerce')


# --- 4. FACTBASE API (Jusqu'à Mai 2026) ---
print("4/4 - Factbase...")
try:
    df4 = pd.read_csv('trump_factbase_2026_04h05m42s.csv', on_bad_lines='skip', engine='python')
except TypeError:
    df4 = pd.read_csv('trump_factbase_2026_04h05m42s.csv', error_bad_lines=False, engine='python')

df4 = df4.rename(columns=lambda x: x.replace(';;;', ''))
df4 = df4[['id', 'date', 'text', 'likes', 'shares']]
# Conversion de date spécifique (Format ISO 8601)
df4['date'] = pd.to_datetime(df4['date'], utc=True, errors='coerce')


# --- 5. FUSION TOTALE ---
print("\nAssemblage final...")
df_master = pd.concat([df1, df2, df3, df4], ignore_index=True)

# Application des fonctions (et on laisse tomber likes/shares comme convenu)
df_master = df_master[['id', 'date', 'text']]

# On supprime les lignes qui n'ont VRAIMENT pas de date ni de texte
df_master = df_master.dropna(subset=['date', 'text'])

# Tri par date et dédoublonnage intelligent
print("Tri chronologique et dédoublonnage...")
df_master = df_master.sort_values(by='date')
df_master = df_master.drop_duplicates(subset=['text'], keep='last')

# Sauvegarde
nom_fichier = "TRUMP_TEXTE_PUR_CORRIGE.csv"
df_master.to_csv(nom_fichier, index=False, encoding='utf-8')

print("\n--- VICTOIRE ! ---")
print(f"Fichier généré : {nom_fichier}")
print(f"Posts récupérés : {len(df_master)}")
print("Vérifie les premières et dernières lignes pour être sûr !")
