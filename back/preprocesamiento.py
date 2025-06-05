import json
import pandas as pd
from nltk.tokenize import word_tokenize, regexp_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

# Descargar recursos necesarios
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

def cargar_corpus():

    # Ruta del archivo corpus.jsonl
    ruta_corpus = r"\gaming\corpus.jsonl"
    corpusdf = pd.read_json(ruta_corpus, lines=True)

    return corpusdf

def preprocesar_texto():

    # Cargar el corpus
    corpusdf = cargar_corpus()

    # Normalizar con expresiones regulares
    corpusdf['regex_tokens'] = corpusdf['text'].str.lower().apply(
        lambda x: regexp_tokenize(x, pattern=r'\w[a-z]+'))

    # Eliminar stopwords
    def remove_stopwords(tokens):
        sw = set(stopwords.words('english'))
        return [t for t in tokens if t not in sw]
    corpusdf['sw_tokens'] = corpusdf['regex_tokens'].apply(remove_stopwords)

    # Lematizar los tokens
    lemmatizer = WordNetLemmatizer()
    corpusdf['lem_tokens'] = corpusdf['sw_tokens'].apply(
        lambda tokens: [lemmatizer.lemmatize(t) for t in tokens])

    # Unir los tokens lematizados en una sola cadena
    corpusdf['preprocesado'] = corpusdf['lem_tokens'].apply(lambda tokens: ' '.join(tokens))

    # Retornar el DataFrame completo con todos los documentos preprocesados
    return corpusdf

#
# Llamar a la función y mostrar solo el primer documento preprocesado
#corpus_normalizado = cargar_corpus()
#print('DOC NORMAL: ',corpus_normalizado['text'].iloc[0])
#corpus_preprocesado = preprocesar_texto()
#print('DOC PREPROCESADO: ',corpus_preprocesado['preprocesado'].iloc[0])
