import pandas as pd
import networkx as nx
from itertools import combinations
from collections import Counter, defaultdict

# ==============================
# CONFIGURATION
# ==============================

INPUT_FILE = "data/TRUMP_NLP_READY.csv"

OUTPUT_GEXF = "TRUMP_GRAPH_GLOBAL.gexf"
OUTPUT_NODES_CSV = "TRUMP_NODES.csv"
OUTPUT_EDGES_CSV = "TRUMP_EDGES.csv"

# Nombre maximum de mots-clés à garder dans le graphe
TOP_N_KEYWORDS = 250 #500

# Poids minimum d'une arête pour être gardée
MIN_EDGE_WEIGHT = 20 #50


def main():
    print("Lecture du fichier NLP...")
    df = pd.read_csv(INPUT_FILE)

    if "keywords" not in df.columns:
        raise ValueError("La colonne 'keywords' est introuvable dans le fichier.")

    df["keywords"] = df["keywords"].fillna("").astype(str)

    print(f"Lignes chargées : {len(df)}")

    # ==============================
    # 1. Compter la fréquence des mots
    # ==============================

    keyword_counter = Counter()

    for keywords in df["keywords"]:
        words = keywords.split()
        keyword_counter.update(words)

    print(f"Nombre total de keywords uniques : {len(keyword_counter)}")

    # Garder les mots les plus fréquents
    top_keywords = set(
        word for word, count in keyword_counter.most_common(TOP_N_KEYWORDS)
    )

    print(f"Keywords gardés pour le graphe : {len(top_keywords)}")

    # ==============================
    # 2. Construire les cooccurrences
    # ==============================

    edge_counter = defaultdict(int)

    for keywords in df["keywords"]:
        words = keywords.split()

        # On garde uniquement les top keywords
        words = [word for word in words if word in top_keywords]

        # On retire les doublons dans un même post pour éviter les liens artificiels
        unique_words = sorted(set(words))

        # Si moins de 2 mots, impossible de créer une relation
        if len(unique_words) < 2:
            continue

        # Créer une arête entre chaque paire de mots présents dans le même post
        for word1, word2 in combinations(unique_words, 2):
            edge_counter[(word1, word2)] += 1

    print(f"Nombre d'arêtes avant filtrage : {len(edge_counter)}")

    # ==============================
    # 3. Créer le graphe NetworkX
    # ==============================

    G = nx.Graph()

    # Ajouter les noeuds
    for word in top_keywords:
        G.add_node(
            word,
            label=word,
            frequency=int(keyword_counter[word])
        )

    # Ajouter les arêtes avec un poids minimum
    kept_edges = 0

    for (word1, word2), weight in edge_counter.items():
        if weight >= MIN_EDGE_WEIGHT:
            G.add_edge(
                word1,
                word2,
                weight=int(weight)
            )
            kept_edges += 1

    print(f"Noeuds dans le graphe : {G.number_of_nodes()}")
    print(f"Arêtes gardées : {kept_edges}")

    # ==============================
    # 4. Calculer quelques mesures
    # ==============================

    print("Calcul des mesures de centralité...")

    degree_dict = dict(G.degree())
    weighted_degree_dict = dict(G.degree(weight="weight"))

    nx.set_node_attributes(G, degree_dict, "degree")
    nx.set_node_attributes(G, weighted_degree_dict, "weighted_degree")

    # ==============================
    # 5. Exporter pour Gephi
    # ==============================

    nx.write_gexf(G, OUTPUT_GEXF)

    print(f"Fichier Gephi créé : {OUTPUT_GEXF}")

    # ==============================
    # 6. Exporter aussi en CSV
    # ==============================

    nodes_data = []

    for node, data in G.nodes(data=True):
        nodes_data.append({
            "id": node,
            "label": data.get("label", node),
            "frequency": data.get("frequency", 0),
            "degree": data.get("degree", 0),
            "weighted_degree": data.get("weighted_degree", 0)
        })

    edges_data = []

    for source, target, data in G.edges(data=True):
        edges_data.append({
            "source": source,
            "target": target,
            "weight": data.get("weight", 1)
        })

    pd.DataFrame(nodes_data).to_csv(OUTPUT_NODES_CSV, index=False)
    pd.DataFrame(edges_data).to_csv(OUTPUT_EDGES_CSV, index=False)

    print(f"Fichier noeuds créé : {OUTPUT_NODES_CSV}")
    print(f"Fichier arêtes créé : {OUTPUT_EDGES_CSV}")

    print("\nPhase 3 terminée avec succès.")


if __name__ == "__main__":
    main()