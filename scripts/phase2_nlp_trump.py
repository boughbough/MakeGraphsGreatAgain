"""
Phase 2 NLP - Projet MIAGE Trump rhetoric graph
Entrée  : TRUMP_TEXTE_PUR_CORRIGE.csv  (colonnes id, date, text)
Sortie  : TRUMP_NLP_READY.csv          (colonnes id, date, keywords)

Utilisation recommandée :
    pip install pandas spacy
    python -m spacy download en_core_web_sm
    python phase2_nlp_trump.py

Le script utilise en_core_web_sm si le modèle est installé. Sinon, il garde le tokenizer
SpaCy et applique une lemmatisation légère de secours pour pouvoir produire un livrable.
"""

from __future__ import annotations

import html
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Iterable, List

import pandas as pd
import spacy
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS

INPUT_PATH = Path("TRUMP_TEXTE_PUR_CORRIGE.csv")
OUTPUT_PATH = Path("TRUMP_NLP_READY.csv")

# Nettoyage des liens, mentions, caractères parasites.
BROKEN_SOCIAL_URL_RE = re.compile(
    r"https?\s*:\s*/\s*/\s*(?:truthsocial|twitter|x)\.com(?:\s*/?\s*[A-Za-z0-9_@.-]+)+",
    flags=re.IGNORECASE,
)
URL_RE = re.compile(
    r"(?:https?\s*:\s*/\s*/\s*\S+)|(?:www\.\S+)|(?:\b\S+\.(?:com|org|net|gov|edu|io|co|us)\S*\b)",
    flags=re.IGNORECASE,
)
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")
NON_TEXT_RE = re.compile(r"[^A-Za-z\s'-]")
MULTISPACE_RE = re.compile(r"\s+")

CUSTOM_STOPWORDS = {
    # Bruit technique / plateformes / artefacts de scraping
    "amp", "http", "https", "www", "com", "org", "net", "html", "truthsocial",
    "twitter", "tweet", "retweet", "rt", "video", "photo", "image", "pic", "link",
    "realdonaldtrump", "realdonaldtru", "donaldjtrump", "truth", "social",
    "user", "users", "status", "statuses", "statuse",
    # Tokens trop peu informatifs pour un graphe rhétorique
    "today", "tomorrow", "tonight", "yesterday", "morning", "afternoon", "evening",
}

STOPWORDS = set(STOP_WORDS) | CUSTOM_STOPWORDS

# Quelques irréguliers utiles pour éviter les nœuds doublons dans le graphe.
IRREGULAR_LEMMAS = {
    "failing": "fail", "failed": "fail", "fails": "fail",
    "winning": "win", "won": "win", "wins": "win",
    "running": "run", "ran": "run", "runs": "run",
    "making": "make", "made": "make", "makes": "make",
    "taking": "take", "took": "take", "taken": "take", "takes": "take",
    "giving": "give", "gave": "give", "given": "give", "gives": "give",
    "getting": "get", "got": "get", "gets": "get",
    "going": "go", "went": "go", "goes": "go",
    "coming": "come", "came": "come", "comes": "come",
    "lying": "lie", "lied": "lie", "lies": "lie",
    "dying": "die", "died": "die", "dies": "die",
    "voting": "vote", "voted": "vote", "votes": "vote",
    "elections": "election", "policies": "policy", "countries": "country",
    "stories": "story", "cities": "city", "parties": "party",
    "democrats": "democrat", "republicans": "republican",
    "children": "child", "men": "man", "women": "woman",
    "better": "good", "best": "good", "worse": "bad", "worst": "bad",
    "media": "media", "news": "news",
}

POS_TO_KEEP = {"NOUN", "PROPN", "VERB", "ADJ", "ADV"}


def normalize_text(text: str) -> str:
    """Supprime URLs, mentions, ponctuation et normalise les espaces."""
    text = html.unescape(str(text))
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = BROKEN_SOCIAL_URL_RE.sub(" ", text)
    text = URL_RE.sub(" ", text)
    text = MENTION_RE.sub(" ", text)
    text = HASHTAG_RE.sub(r"\1", text)  # #MAGA -> MAGA, car le hashtag peut porter du sens
    text = text.replace("'", " ")
    text = NON_TEXT_RE.sub(" ", text)
    text = MULTISPACE_RE.sub(" ", text).strip()
    return text


def light_lemma(word: str) -> str:
    """Lemmatisation légère de secours si le modèle SpaCy complet n'est pas installé."""
    if word in IRREGULAR_LEMMAS:
        return IRREGULAR_LEMMAS[word]

    if len(word) <= 3:
        return word

    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"

    if word.endswith("ing") and len(word) > 5:
        base = word[:-3]
        if len(base) > 2 and base[-1] == base[-2]:
            base = base[:-1]
        return base

    if word.endswith("ed") and len(word) > 4:
        base = word[:-2]
        if len(base) > 2 and base[-1] == base[-2]:
            base = base[:-1]
        return IRREGULAR_LEMMAS.get(word, base)

    if word.endswith("es") and len(word) > 4:
        if word.endswith(("ches", "shes", "sses", "xes", "zzes", "oes")):
            return word[:-2]

    if word.endswith("s") and len(word) > 4 and not word.endswith(("ss", "ous", "ius", "news")):
        return word[:-1]

    return word


def load_pipeline():
    """Charge SpaCy complet si possible, sinon SpaCy tokenizer + fallback."""
    try:
        nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
        return nlp, True
    except OSError:
        nlp = English()
        return nlp, False


def tokens_to_keywords(doc, has_pos_model: bool) -> List[str]:
    keywords: List[str] = []

    for token in doc:
        if token.is_space or token.like_url or token.like_email:
            continue

        raw = token.text.lower().strip("-'")
        if not raw or len(raw) <= 2 or raw in STOPWORDS:
            continue
        if not raw.isalpha():
            continue

        if has_pos_model:
            if token.pos_ not in POS_TO_KEEP:
                continue
            lemma = token.lemma_.lower().strip("-'")
        else:
            lemma = light_lemma(raw)

        if len(lemma) <= 2 or lemma in STOPWORDS or not lemma.isalpha():
            continue

        keywords.append(lemma)

    return keywords


def build_keywords(texts: Iterable[str], nlp, has_pos_model: bool) -> List[str]:
    cleaned_texts = (normalize_text(t) for t in texts)
    results: List[str] = []

    for doc in nlp.pipe(cleaned_texts, batch_size=1000):
        kws = tokens_to_keywords(doc, has_pos_model)
        # On garde les répétitions : utile pour étudier la répétition rhétorique.
        results.append(" ".join(kws))

    return results


def main() -> None:
    df = pd.read_csv(INPUT_PATH)
    expected = {"id", "date", "text"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans le CSV : {missing}")

    df = df[["id", "date", "text"]].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True, format="mixed")
    if df["date"].isna().any():
        raise ValueError("Certaines dates sont invalides après conversion.")

    nlp, has_pos_model = load_pipeline()
    print("Pipeline NLP :", "SpaCy en_core_web_sm" if has_pos_model else "SpaCy tokenizer + fallback léger")

    df["keywords"] = build_keywords(df["text"], nlp, has_pos_model)
    out = df[["id", "date", "keywords"]].copy()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d %H:%M:%S%z")
    out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    empty_count = int((out["keywords"].str.len() == 0).sum())
    token_counter = Counter(" ".join(out["keywords"]).split())

    print(f"Lignes traitées : {len(out):,}".replace(",", " "))
    print(f"Lignes sans keyword après nettoyage : {empty_count:,}".replace(",", " "))
    print("Top 25 keywords :")
    for word, count in token_counter.most_common(25):
        print(f"  {word}: {count}")
    print(f"Fichier créé : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
