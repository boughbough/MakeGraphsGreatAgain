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

###########################################
## CHANGER LA TARGET ICI
###########################################
TARGET = "OBAMA"
FOLDER = TARGET.lower()

INPUT_PATH = Path(f"data/csv/{FOLDER}/{TARGET}_TWEETS.csv")
OUTPUT_PATH = Path(f"data/csv/{FOLDER}/{TARGET}_NLP_READY.csv")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

BROKEN_SOCIAL_URL_RE = re.compile(r"https?\s*:\s*/\s*/\s*(?:truthsocial|twitter|x)\.com(?:\s*/?\s*[A-Za-z0-9_@.-]+)+", flags=re.IGNORECASE)
URL_RE = re.compile(r"(?:https?\s*:\s*/\s*/\s*\S+)|(?:www\.\S+)|(?:\b\S+\.(?:com|org|net|gov|edu|io|co|us)\S*\b)", flags=re.IGNORECASE)
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")
NON_TEXT_RE = re.compile(r"[^A-Za-z\s'-]")
MULTISPACE_RE = re.compile(r"\s+")

BASE_STOPWORDS = {
    "amp", "http", "https", "www", "com", "org", "net", "html", "twitter", "tweet", 
    "retweet", "rt", "video", "photo", "image", "pic", "link", "truthsocial", "social",
    "today", "tomorrow", "tonight", "yesterday", "morning", "afternoon", "evening",
}

TARGET_STOPWORDS = {
    "TRUMP": {"realdonaldtrump", "donaldjtrump", "trump"},
    "BIDEN": {"joebiden", "potus", "biden"},
    "OBAMA": {"barackobama", "obama", "presidentobama"},
}

STOPWORDS = set(STOP_WORDS) | BASE_STOPWORDS | TARGET_STOPWORDS.get(TARGET, set())

IRREGULAR_LEMMAS = {
    "failing": "fail", "failed": "fail", "fails": "fail", "winning": "win", "won": "win",
    "making": "make", "made": "make", "taking": "take", "giving": "give", "getting": "get",
    "democrats": "democrat", "republicans": "republican", "media": "media", "news": "news",
    "children": "child", "men": "man", "women": "woman", "better": "good", "best": "good",
}

POS_TO_KEEP = {"NOUN", "PROPN", "VERB", "ADJ", "ADV"}

def normalize_text(text: str) -> str:
    text = html.unescape(str(text))
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = URL_RE.sub(" ", MENTION_RE.sub(" ", BROKEN_SOCIAL_URL_RE.sub(" ", text)))
    text = HASHTAG_RE.sub(r"\1", text).replace("'", " ")
    return MULTISPACE_RE.sub(" ", NON_TEXT_RE.sub(" ", text)).strip()

def light_lemma(word: str) -> str:
    if word in IRREGULAR_LEMMAS: return IRREGULAR_LEMMAS[word]
    if len(word) <= 3: return word
    if word.endswith("ies") and len(word) > 4: return word[:-3] + "y"
    if word.endswith("s") and len(word) > 4 and not word.endswith(("ss", "ous", "news")): return word[:-1]
    return word

def load_pipeline():
    try:
        return spacy.load("en_core_web_sm", disable=["ner", "parser"]), True
    except OSError:
        return English(), False

def tokens_to_keywords(doc, has_pos_model: bool) -> List[str]:
    keywords = []
    for token in doc:
        raw = token.text.lower().strip("-'")
        if not raw or len(raw) <= 2 or raw in STOPWORDS or not raw.isalpha(): continue
        if has_pos_model:
            if token.pos_ not in POS_TO_KEEP: continue
            lemma = token.lemma_.lower().strip("-'")
        else:
            lemma = light_lemma(raw)
        if len(lemma) <= 2 or lemma in STOPWORDS: continue
        keywords.append(lemma)
    return keywords

def main() -> None:
    if not INPUT_PATH.exists():
        print(f"Erreur : Le fichier {INPUT_PATH} n'existe pas.")
        return

    df = pd.read_csv(INPUT_PATH)
    nlp, has_pos_model = load_pipeline()
    
    print(f"Traitement NLP de {TARGET} ({len(df)} lignes)...")
    cleaned_texts = (normalize_text(t) for t in df["text"])
    
    results = []
    for doc in nlp.pipe(cleaned_texts, batch_size=1000):
        results.append(" ".join(tokens_to_keywords(doc, has_pos_model)))

    df["keywords"] = results
    df[["id", "date", "keywords"]].to_csv(OUTPUT_PATH, index=False)
    
    print(f"Fichier créé : {OUTPUT_PATH}")
    print(f"Top 10 keywords pour {TARGET} :")
    token_counter = Counter(" ".join(results).split())
    for word, count in token_counter.most_common(10):
        print(f"  {word}: {count}")

if __name__ == "__main__":
    main()