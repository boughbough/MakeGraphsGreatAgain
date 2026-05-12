import requests
import pandas as pd
import time
import datetime

print("Aspiration de l'API Factbase...")

base_url = "https://rollcall.com/wp-json/factbase/v1/twitter?platform=all&sort=date&sort_order=desc&page={}&format=json"

donnees = []
page = 1
max_pages = 200

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
}

while page <= max_pages:
    print(f"Aspiration de la page {page}...")
    url = base_url.format(page)
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Arrêt : Le serveur a répondu avec le code {response.status_code}")
            break
            
        data = response.json()
        
        posts = data.get('data', data) if isinstance(data, dict) else data
        
        if not posts or len(posts) == 0:
            print("Plus aucun post trouvé. Fin de la collecte !")
            break
            
        for post in posts:

            texte = post.get('text') or post.get('full_text') or post.get('content')
            
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
        time.sleep(1)
        
    except Exception as e:
        print(f"Erreur sur la page {page} : {e}")
        break

if len(donnees) > 0:
    df = pd.DataFrame(donnees)
    
    df = df.dropna(subset=['text'])
    df = df.drop_duplicates(subset=['id'])
    
    heure_actuelle = datetime.datetime.now().strftime("%Hh%Mm%Ss")
    nom_fichier = f"data/csv/trump/TRUMP_TWEETS_FACTBASE.csv"
    
    df.to_csv(nom_fichier, index=False, encoding='utf-8')
    print(f"{len(df)} posts récupérés proprement !")
    print(f"Fichier sauvegardé : {nom_fichier}")
else:
    print("\nAucun post n'a été récupéré.")