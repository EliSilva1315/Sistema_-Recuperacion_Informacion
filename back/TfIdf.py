from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class TFIDFSearchEngine:
    def __init__(self, texts, documents_data, max_features=10000):
        """
        Inicializa el motor TF-IDF con los textos preprocesados y los datos de documentos.

        Args:
            texts (list): Lista de textos preprocesados del corpus.
            documents_data (list): Metadatos y campos de los documentos.
            max_features (int): Número máximo de características TF-IDF.
        """
        self.documents_data = documents_data
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words=None,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            token_pattern=r'\b\w+\b'
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)

    def search(self, query, limit=10, threshold=0.1):
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        sorted_indices = np.argsort(similarities)[::-1]

        results = []
        for idx in sorted_indices:
            score = similarities[idx]
            if score < threshold:
                break
            doc = self.documents_data[idx].copy()
            doc['similarity_score'] = float(score)
            doc['rank'] = len(results) + 1
            if 'text_original' in doc:
                doc['preview'] = doc['text_original'][:200] + "..." if len(doc['text_original']) > 200 else doc['text_original']
            results.append(doc)
            if len(results) >= limit:
                break
        return results

    def get_vectorizer(self):
        return self.vectorizer

    def get_matrix(self):
        return self.tfidf_matrix
