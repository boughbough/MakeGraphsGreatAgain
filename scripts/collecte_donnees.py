from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
import pandas as pd
import time
import datetime

# 1. CONFIGURATION EDGE
options = EdgeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Edge(options=options)

try:
    print("Ouverture de Microsoft Edge sur Truth Social...")
    driver.get("https://truthsocial.com/@realDonaldTrump")
    
    # --- PAUSE CONNEXION ---
    print("\n--- ACTION REQUISE ---")
    print("1. Connecte-toi à ton compte.")
    print("2. Descends un peu pour charger les premiers posts.")
    input("3. Appuie sur ENTRÉE ici pour lancer le grand moissonnage...")

    donnees_extraites = []
    ids_deja_vus = set()
    nb_scrolls = 2000
    
    for i in range(nb_scrolls):
        print(f"Collecte : Scroll {i+1}/{nb_scrolls}... (Posts récupérés : {len(donnees_extraites)})")
        
        # On cible le texte comme point d'ancrage
        text_elements = driver.find_elements(By.CSS_SELECTOR, ".status__content, [data-testid='status-content']")
        
        for text_el in text_elements:
            try:
                texte = text_el.text.replace('\n', ' ').strip()
                if len(texte) < 15:
                    continue 
                    
                # -- A. EXTRACTION DE LA DATE --
                try:
                    time_el = text_el.find_element(By.XPATH, "./ancestor::div[.//time][1]//time")
                    date_post = time_el.get_attribute("datetime") or time_el.get_attribute("title") or time_el.text
                except:
                    continue # Sans date, on ignore le post
                
                if not date_post or str(date_post).strip() == "None":
                    continue

                # -- B. EXTRACTION DES LIKES ET SHARES --
                # On remonte au conteneur principal du post, puis on cherche la barre d'action
                likes = "0"
                shares = "0"
                try:
                    # Sur Mastodon/Truth, les boutons ont souvent ces attributs ou sont dans un ordre précis
                    # Bouton ReTruth (souvent le 2ème bouton ou contient 'reblog')
                    shares_el = text_el.find_element(By.XPATH, "./following::button[contains(@class, 'reply-indicator') or contains(@data-testid, 'reblog') or contains(@aria-label, 'ReTruth')][1]")
                    shares = shares_el.text.strip()
                    if shares == '': shares = "0"
                    
                    # Bouton Like (souvent le 3ème bouton ou contient 'favourite')
                    likes_el = text_el.find_element(By.XPATH, "./following::button[contains(@class, 'star-icon') or contains(@data-testid, 'favourite') or contains(@aria-label, 'Like')][1]")
                    likes = likes_el.text.strip()
                    if likes == '': likes = "0"
                except Exception:
                    # Si la structure HTML a un peu changé pour ce post, on garde "0" par sécurité
                    pass

                # -- C. SAUVEGARDE --
                post_id = f"{str(date_post).replace(' ', '_')}_{texte[:10]}"
                
                if post_id not in ids_deja_vus:
                    ids_deja_vus.add(post_id)
                    donnees_extraites.append({
                        "id": post_id,
                        "date": date_post,
                        "text": texte,
                        "likes": likes,
                        "shares": shares
                    })
            except Exception:
                continue
        
        # On descend
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3) # Pause cruciale pour laisser le réseau charger les images/chiffres

    # 4. SAUVEGARDE BLINDÉE
    df = pd.DataFrame(donnees_extraites)
    heure_actuelle = datetime.datetime.now().strftime("%Hh%Mm%Ss")
    nom_fichier = f"trump_data_oct25_mar26_COMPLET_{heure_actuelle}.csv"
    
    df.to_csv(nom_fichier, index=False, encoding='utf-8')
    
    print(f"\n--- VICTOIRE ---")
    print(f"{len(df)} posts uniques extraits avec Dates, Likes et Shares !")
    print(f"Sauvegardé sous : {nom_fichier}")

except Exception as e:
    print(f"Une erreur est survenue : {e}")
finally:
    driver.quit()