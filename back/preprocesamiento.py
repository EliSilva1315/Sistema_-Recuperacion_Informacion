import json
import pandas as pd
from nltk.tokenize import word_tokenize, regexp_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
from cargar_corpus import cargar_corpus 

# Descargar recursos necesarios
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


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
    
    #semantizar los tokens 
    semantizar_token = lambda token: token 
    corpusdf['sem_tokens'] = corpusdf['lem_tokens'].apply(
        lambda tokens: [semantizar_token(t) for t in tokens])
    
    # Unir los tokens lematizados en una sola cadena
    corpusdf['preprocesado'] = corpusdf['sem_tokens'].apply(lambda tokens: ' '.join(tokens))

    # Retornar el DataFrame completo con todos los documentos preprocesados
    return corpusdf

