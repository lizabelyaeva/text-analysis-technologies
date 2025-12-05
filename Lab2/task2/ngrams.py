import re
from collections import Counter
from bs4 import BeautifulSoup

TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яёЁ0-9\+\#\-]+")
DEFAULT_STOPWORDS = {
    "и","в","во","не","на","с","со","как","а","к","по","для","что","он","она",
    "они","это","все","наш","свой","из","за","от","до","при","о","об","его","ее",
    "им","у","их","быть","есть","будет","требуется","требуется:","можно","опыт",
    "and","or","the","a","an","to","of","with","in","for","on","is","are","we","you",
    "условия","обязанности","требования","ответственность","знание","желательно",
    "работы","работы:","работы.","skills","experience","responsibility","requirements"
}

def clean_text(text):
    if not text:
        return ""

    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text(separator=" ")

    # Удаляем нумерацию (1. 2) 3.1 etc.)
    text = re.sub(r"\b\d+(\.\d+)*[\)\.:]?", " ", text)

    # Убираем служебные символы
    text = re.sub(r"[•–—_/]", " ", text)

    # Схлопываем пробелы
    text = re.sub(r"\s+", " ", text).strip()

    return text

def tokenize(text):
    return [t.lower() for t in TOKEN_RE.findall(text)]

def build_ngrams(tokens, n):
    if n <= 0 or len(tokens) < n:
        return []
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

def extract_ngrams_from_snippets(vacancies, stopwords=None, top_k=None):
    stop = set(stopwords) if stopwords else DEFAULT_STOPWORDS
    counters = {1: Counter(), 2: Counter(), 3: Counter()}

    for v in vacancies:
        snippet = v.get("snippet") or {}
        requirement = snippet.get("requirement") or ""
        responsibility = snippet.get("responsibility") or ""
        text = clean_text(requirement + " " + responsibility)
        tokens = [t for t in tokenize(text) if t not in stop and len(t) > 1]
        for n in (1,2,3):
            counters[n].update(build_ngrams(tokens, n))

    if top_k is None:
        return {n: list(counters[n].items()) for n in counters}  # все n-граммы
    return {n: counters[n].most_common(top_k) for n in counters}

def save_counter_csv(counter_items, path):
    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ngram", "count"])
        for k,v in counter_items:
            writer.writerow([k, v])
