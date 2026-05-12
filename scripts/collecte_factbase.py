import requests
import pandas as pd
import time
import datetime

print("Démarrage de l'aspiration de l'API Factbase...")

# L'URL magique (on a remplacé "page=1" par "page={}" pour pouvoir boucler)
base_url = "https://rollcall.com/wp-json/factbase/v1/twitter?platform=all&sort=date&sort_order=desc&page={}&format=json"

donnees = []
page = 1
max_pages = 200 # Sécurité : on aspire max 200 pages (soit des milliers de posts)

# On se fait passer pour un vrai navigateur pour éviter les blocages de sécurité
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
}

while page <= max_pages:
    print(f"Aspiration de la page {page}...")
    url = base_url.format(page)
    
    try:
        response = requests.get(url, headers=headers)
        
        # Si le serveur nous dit "Non" ou "Introuvable"
        if response.status_code != 200:
            print(f"Arrêt : Le serveur a répondu avec le code {response.status_code}")
            break
            
        data = response.json()
        
        # Factbase peut renvoyer une liste directe ou un dictionnaire contenant les données
        posts = data.get('data', data) if isinstance(data, dict) else data
        
        # Si la liste est vide, on a atteint la fin de l'historique !
        if not posts or len(posts) == 0:
            print("Plus aucun post trouvé. Fin de la collecte !")
            break
            
        for post in posts:
            # La beauté du JSON : on utilise .get() pour attraper les infos
            # J'ai mis plusieurs clés possibles au cas où leur base de données varie
            texte = post.get('text') or post.get('full_text') or post.get('content')
            
            # On ignore les textes vides ou les Retweets directs
            if not texte or str(texte).startswith("RT @"):
                continue
                
            post_id = post.get('id') or post.get('id_str')
            date_post = post.get('created_at') or post.get('date')
            likes = post.get('favorite_count') or post.get('likes') or 0
            shares = post.get('retweet_count') or post.get('reblogs') or 0
            
            donnees.append({
                "id": post_id,
                "date": date_post,
                "text": texte,
                "likes": likes,
                "shares": shares
            })
            
        page += 1
        time.sleep(1) # Pause éthique de 1 seconde
        
    except Exception as e:
        print(f"Erreur sur la page {page} : {e}")
        break

# --- SAUVEGARDE DE LA DATA ---
if len(donnees) > 0:
    df = pd.DataFrame(donnees)
    
    # Nettoyage de sécurité
    df = df.dropna(subset=['text'])
    df = df.drop_duplicates(subset=['id'])
    
    heure_actuelle = datetime.datetime.now().strftime("%Hh%Mm%Ss")
    nom_fichier = f"trump_factbase_2026_{heure_actuelle}.csv"
    
    df.to_csv(nom_fichier, index=False, encoding='utf-8')
    print(f"\n--- VICTOIRE TOTALE ---")
    print(f"{len(df)} posts récupérés proprement !")
    print(f"Fichier sauvegardé : {nom_fichier}")
else:
    print("\nAucun post n'a été récupéré. Le format du JSON est peut-être différent de ce qu'on attendait.")