import pandas as pd
import networkx as nx
import json
from community import community_louvain
from itertools import combinations
from collections import Counter

MIN_COUNT = 60
MIN_EDGE_WEIGHT = 15
MAX_NODES = 250
TOP_K_LINKS = 5

###########################################
## CHANGER LA TARGET ICI
###########################################
TARGET = "OBAMA"

if TARGET == "TRUMP":
    INPUT_FILE = "data/csv/trump/TRUMP_NLP_READY.csv"
    OUTPUT_FILE = "data/json/trump_3d_data.json"
elif TARGET == "BIDEN":
    INPUT_FILE = "data/csv/biden/BIDEN_NLP_READY.csv"
    OUTPUT_FILE = "data/json/biden_3d_data.json"
elif TARGET == "OBAMA":
    INPUT_FILE = "data/csv/obama/OBAMA_NLP_READY.csv"
    OUTPUT_FILE = "data/json/obama_3d_data.json"
else:
    print(f"Erreur : Target {TARGET} non reconnue.")
    exit()

print(f"--- Génération du graphe pour {TARGET} ---")

df = pd.read_csv(INPUT_FILE)
df['keywords'] = df['keywords'].fillna("")

all_words = " ".join(df['keywords']).split()
word_counts = Counter(all_words)
top_words = [word for word, count in word_counts.most_common(MAX_NODES) if count >= MIN_COUNT]

G_full = nx.Graph()
for keywords in df['keywords']:
    words = sorted(list(set(keywords.split())))
    filtered = [w for w in words if w in top_words]
    for u, v in combinations(filtered, 2):
        if G_full.has_edge(u, v):
            G_full[u][v]['weight'] += 1
        else:
            G_full.add_edge(u, v, weight=1)

final_edges = set()
for node in G_full.nodes():
    neighbors = sorted(G_full[node].items(), key=lambda x: x[1]['weight'], reverse=True)
    for neighbor, data in neighbors[:TOP_K_LINKS]:
        if data['weight'] >= MIN_EDGE_WEIGHT:
            final_edges.add(tuple(sorted((node, neighbor))))

G = nx.Graph()
G.add_edges_from([(u, v, G_full[u][v]) for u, v in final_edges])
G.remove_nodes_from(list(nx.isolates(G)))

partition_raw = community_louvain.best_partition(G, resolution=1.1)

counts = Counter(partition_raw.values())
sorted_groups = [g for g, c in counts.most_common()]
mapping = {old_id: new_id for new_id, old_id in enumerate(sorted_groups)}

partition = {}
for node, old_id in partition_raw.items():
    new_id = mapping[old_id]
    partition[node] = new_id if new_id < 4 else 99

centrality = nx.degree_centrality(G)

nodes = []
for node in G.nodes():
    nodes.append({
        "id": node,
        "name": node.upper(),
        "group": partition[node],
        "val": word_counts[node],
        "centrality": centrality[node]
    })

links = [{"source": u, "target": v, "value": d['weight']} for u, v, d in G.edges(data=True)]

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump({"nodes": nodes, "links": links}, f, ensure_ascii=False)

print(f"Terminé ! {len(nodes)} nœuds et {len(links)} liens enregistrés dans {OUTPUT_FILE}.")