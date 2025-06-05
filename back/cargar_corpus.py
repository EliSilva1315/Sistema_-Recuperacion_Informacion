import json
import pandas as pd

def cargar_corpus():

    # Ruta del archivo corpus.jsonl
    ruta_corpus = "gaming/corpus.jsonl"
    corpusdf = pd.read_json(ruta_corpus, lines=True)

    return corpusdf
