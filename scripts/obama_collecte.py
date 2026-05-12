import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

base_url = "https://polititweet.org/tweets?account=813286"
all_data = []

total_pages = 156

print(f"Début du scraping pour Barack Obama ({total_pages} pages)...")

months = {
    'January': '01', 'February': '02', 'March': '03', 'April': '04',
    'May': '05', 'June': '06', 'July': '07', 'August': '08',
    'September': '09', 'October': '10', 'November': '11', 'December': '12'
}

for page in range(1, total_pages + 1):
    url = f"{base_url}&page={page}"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        containers = soup.find_all('div', class_='column')
        
        for container in containers:
            p_text = container.find('p', class_='small-top-margin')
            if not p_text: continue
            
            raw_text = p_text.get_text(strip=True).split('—')[0].strip()
            
            date_tag = container.find('span', class_='tag')
            clean_date = "2024-01-01 00:00:00"
            
            if date_tag:
                date_str = date_tag.get_text(strip=True).replace('Posted ', '')
                try:
                    for month_name, month_num in months.items():
                        if month_name in date_str:
                            date_str = date_str.replace(month_name, month_num)
                    
                    date_obj = datetime.strptime(date_str.replace(',', ''), '%m %d %Y')
                    clean_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass

            tweet_id = f"obama_{page}_{len(all_data)}"

            if len(raw_text) > 10:
                all_data.append({
                    'id': tweet_id,
                    'date': clean_date,
                    'text': raw_text
                })
            
        print(f"Page {page}/{total_pages} terminée ({len(all_data)} tweets collectés)")
        time.sleep(1)
        
    except Exception as e:
        print(f"Erreur sur la page {page}: {e}")

df = pd.DataFrame(all_data)
df.to_csv('data/csv/obama/OBAMA_TWEETS.csv', index=False, encoding='utf-8')

print(f"\nFichier .csv prêt! ({len(all_data)} lignes.)")