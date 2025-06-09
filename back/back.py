from flask import Flask, jsonify, request
from flask_cors import CORS
from preprocesamiento import preprocesar_texto
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
import json
from collections import Counter
import time

app = Flask(__name__)
CORS(app)

# Variables globales para el sistema
corpus_preprocesado = None
vectorizer = None
tfidf_matrix = None
bm25_model = None
tokenized_corpus = None
documents_data = []

def inicializar_sistema():
    """Inicializa el sistema preprocesando el corpus y creando matrices TF-IDF y BM25"""
    global corpus_preprocesado, vectorizer, tfidf_matrix, bm25_model, tokenized_corpus, documents_data
    
    try:
        print("🔄 Iniciando preprocesamiento del corpus...")
        corpus_preprocesado = preprocesar_texto()
        
        if corpus_preprocesado is None or corpus_preprocesado.empty:
            print("❌ Error: Corpus preprocesado está vacío")
            return False
        
        print(f"✅ Corpus preprocesado: {len(corpus_preprocesado)} documentos")
        
        # Crear lista de textos para vectorización TF-IDF
        texts_for_vectorization = corpus_preprocesado['preprocesado'].tolist()
        
        # Crear vectorizador TF-IDF
        print("🔄 Creando vectorizador TF-IDF...")
        vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words=None,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            token_pattern=r'\b\w+\b'
        )
        
        # Crear matriz TF-IDF
        tfidf_matrix = vectorizer.fit_transform(texts_for_vectorization)
        print(f"✅ Matriz TF-IDF creada: {tfidf_matrix.shape}")
        
        # Crear modelo BM25
        print("🔄 Creando modelo BM25...")
        # Tokenizar el corpus para BM25 (usa tokens ya lematizados)
        tokenized_corpus = [doc.split() for doc in texts_for_vectorization]
        bm25_model = BM25Okapi(tokenized_corpus)
        print(f"✅ Modelo BM25 creado con {len(tokenized_corpus)} documentos")
        
        # Preparar datos de documentos
        documents_data = []
        for idx, row in corpus_preprocesado.iterrows():
            doc_data = {
                'id': idx,
                'title': row.get('title', f'Documento {idx}'),
                'text_original': row.get('text', ''),
                'text_preprocesado': row.get('preprocesado', ''),
                'tokens': row.get('lem_tokens', [])
            }
            documents_data.append(doc_data)
        
        print(f"✅ Sistema inicializado con TF-IDF + BM25")
        return True
        
    except Exception as e:
        print(f"❌ Error en la inicialización: {e}")
        import traceback
        traceback.print_exc()
        return False

def preprocesar_query(query):
    """
    Preprocesa la query usando el mismo pipeline que el corpus
    """
    try:
        print(f"\n🔧 PREPROCESANDO QUERY:")
        print("-" * 30)
        print(f"  📝 Query original: '{query}'")
        
        from nltk.tokenize import regexp_tokenize
        from nltk.corpus import stopwords
        from nltk.stem import WordNetLemmatizer
        
        # Normalizar con expresiones regulares (mismo patrón del corpus)
        tokens = regexp_tokenize(query.lower(), pattern=r'\w[a-z]+')
        print(f"  🔤 Tokens después de regex: {tokens}")
        
        # Eliminar stopwords
        sw = set(stopwords.words('english'))
        tokens_sin_sw = [t for t in tokens if t not in sw]
        print(f"  🚫 Tokens sin stopwords: {tokens_sin_sw}")
        
        # Lematizar los tokens
        lemmatizer = WordNetLemmatizer()
        tokens_lemmatizados = [lemmatizer.lemmatize(t) for t in tokens_sin_sw]
        print(f"  🌱 Tokens lematizados: {tokens_lemmatizados}")
        
        # Unir tokens en string
        resultado = ' '.join(tokens_lemmatizados)
        print(f"  ✅ Query final: '{resultado}'")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error en preprocesamiento de query: {e}")
        return query

def busqueda_por_similitud_coseno(query, limit=10, threshold=0.1):
    """
    Realiza búsqueda por similitud coseno
    
    Args:
        query (str): Consulta de búsqueda
        limit (int): Número máximo de resultados
        threshold (float): Umbral mínimo de similitud
    
    Returns:
        list: Lista de documentos ordenados por similitud
    """
    try:
        print("\n" + "="*60)
        print(f"🚀 INICIANDO BÚSQUEDA")
        print("="*60)
        
        # Preprocesar la query igual que el corpus
        processed_query = preprocesar_query(query)
        print(f"🔍 Query original: '{query}'")
        print(f"🔍 Query preprocesada: '{processed_query}'")
        
        if not processed_query.strip():
            print("⚠️ Query preprocesada está vacía")
            return []
        
        # Vectorizar la consulta preprocesada
        print(f"\n📊 VECTORIZACIÓN DE LA QUERY")
        print("-" * 40)
        query_vector = vectorizer.transform([processed_query])
        
        # Mostrar información del vector
        print(f"📐 Dimensiones del vector de query: {query_vector.shape}")
        print(f"🔢 Elementos no-cero en el vector: {query_vector.nnz}")
        
        # Mostrar algunos términos y sus pesos TF-IDF
        feature_names = vectorizer.get_feature_names_out()
        query_terms = query_vector.toarray()[0]
        non_zero_indices = np.nonzero(query_terms)[0]
        #hacer tf-idf de la query
        print(f"🏷️ Términos no-cero en la query: {len(non_zero_indices)}")
        print(f"🏷️ Términos únicos en la query: {len(set(feature_names[non_zero_indices]))}")
        print("-" * 40)
        
        print(f"\n🏷️  TÉRMINOS Y PESOS TF-IDF DE LA QUERY:")
        print("-" * 40)
        for idx in non_zero_indices[:10]:  # Mostrar solo los primeros 10
            term = feature_names[idx]
            weight = query_terms[idx]
            print(f"  '{term}': {weight:.4f}")
        if len(non_zero_indices) > 10:
            print(f"  ... y {len(non_zero_indices) - 10} términos más")
        
        # Calcular similitudes coseno
        print(f"\n🧮 CALCULANDO SIMILITUDES COSENO")
        print("-" * 40)
        similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
        
        print(f"📊 Similitudes calculadas: {len(similarities)}")
        print(f"📈 Similitud máxima: {similarities.max():.4f}")
        print(f"📉 Similitud mínima: {similarities.min():.4f}")
        print(f"📊 Similitud promedio: {similarities.mean():.4f}")
        
        # Obtener índices ordenados por similitud (descendente)
        sorted_indices = np.argsort(similarities)[::-1]
        
        print(f"\n🏆 TOP 10 SIMILITUDES:")
        print("-" * 40)
        for i, idx in enumerate(sorted_indices[:10]):
            sim_score = similarities[idx]
            doc_title = documents_data[idx].get('title', f'Documento {idx}')[:50]
            print(f"  {i+1:2d}. Doc {idx:3d}: {sim_score:.4f} - {doc_title}")
        
        print(f"\n🎯 FILTRADO POR UMBRAL >= {threshold}")
        print("-" * 40)
        
        # Filtrar por umbral y límite
        results = []
        for idx in sorted_indices:
            similarity_score = similarities[idx]
            
            # Aplicar umbral mínimo
            if similarity_score < threshold:
                print(f"  🔻 Doc {idx}: {similarity_score:.4f} < {threshold} (omitido)")
                break
                
            # Preparar resultado
            doc = documents_data[idx].copy()
            doc['similarity_score'] = float(similarity_score)
            doc['rank'] = len(results) + 1
            
            # Agregar preview del texto original (primeros 200 caracteres)
            if 'text_original' in doc:
                doc['preview'] = doc['text_original'][:200] + "..." if len(doc['text_original']) > 200 else doc['text_original']
            
            results.append(doc)
            print(f"  ✅ Doc {idx}: {similarity_score:.4f} - {doc.get('title', f'Documento {idx}')[:50]}")
            
            # Aplicar límite
            if len(results) >= limit:
                print(f"  🛑 Límite alcanzado ({limit} resultados)")
                break
        
        print(f"\n✅ RESUMEN FINAL:")
        print("-" * 40)
        print(f"📝 Query original: '{query}'")
        print(f"🔧 Query preprocesada: '{processed_query}'")
        print(f"📊 Documentos procesados: {len(similarities)}")
        print(f"🎯 Umbral usado: {threshold}")
        print(f"🏆 Resultados finales: {len(results)}")
        print(f"⏱️ Mejor similitud: {similarities.max():.4f}")
        print("="*60)
        return results
        
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        import traceback
        traceback.print_exc()
        return []

def busqueda_con_expansion_query(query, limit=10, expansion_terms=3):
    """
    Búsqueda con expansión de consulta usando términos relacionados
    """
    try:
        # Buscar documentos iniciales
        initial_results = busqueda_por_similitud_coseno(query, limit=5, threshold=0.2)
        
        if not initial_results:
            return busqueda_por_similitud_coseno(query, limit, threshold=0.05)
        
        # Extraer términos frecuentes de los mejores resultados
        combined_text = " ".join([
            doc.get('text_preprocesado', '') 
            for doc in initial_results[:3]
        ])
        
        # Encontrar términos más relevantes
        query_expanded = query
        if combined_text:
            from collections import Counter
            # Analizar términos frecuentes del texto preprocesado
            words = combined_text.split()
            word_freq = Counter(words)
            
            # Obtener query preprocesada para comparar
            processed_query = preprocesar_query(query)
            query_words = set(processed_query.split())
            
            # Seleccionar términos nuevos más frecuentes
            top_words = [word for word, freq in word_freq.most_common(expansion_terms * 2) 
                        if word not in query_words and len(word) > 2]
            
            if top_words:
                query_expanded = query + " " + " ".join(top_words[:expansion_terms])
                print(f"🔍 Query expandida: '{query_expanded}'")
        
        # Realizar búsqueda expandida
        return busqueda_por_similitud_coseno(query_expanded, limit, threshold=0.05)
        
    except Exception as e:
        print(f"❌ Error en expansión de consulta: {e}")
        return busqueda_por_similitud_coseno(query, limit, threshold=0.05)

def busqueda_hibrida_tfidf_bm25(query, limit=10, threshold=0.1):
    """
    Realiza búsqueda híbrida comparando TF-IDF y BM25
    """
    try:
        print("\n" + "="*60)
        print(f"🚀 INICIANDO BÚSQUEDA HÍBRIDA TF-IDF + BM25")
        print("="*60)
        
        # Preprocesar la query
        processed_query = preprocesar_query(query)
        query_tokens = processed_query.split()
        
        if not processed_query.strip():
            print("⚠️ Query preprocesada está vacía")
            return []
        
        print(f"🔍 Query original: '{query}'")
        print(f"🔍 Query preprocesada: '{processed_query}'")
        print(f"🔍 Tokens de query: {query_tokens}")
        
        # 1. BÚSQUEDA CON TF-IDF
        print(f"\n📊 EJECUTANDO BÚSQUEDA TF-IDF")
        print("-" * 40)
        
        query_vector = vectorizer.transform([processed_query])
        tfidf_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
        tfidf_sorted_indices = np.argsort(tfidf_similarities)[::-1]
        
        print(f"📈 TF-IDF - Similitud máxima: {tfidf_similarities.max():.4f}")
        print(f"📊 TF-IDF - Similitud promedio: {tfidf_similarities.mean():.4f}")
        
        # 2. BÚSQUEDA CON BM25
        print(f"\n🎯 EJECUTANDO BÚSQUEDA BM25")
        print("-" * 40)
        
        bm25_scores = bm25_model.get_scores(query_tokens)
        bm25_sorted_indices = np.argsort(bm25_scores)[::-1]
        
        print(f"📈 BM25 - Score máximo: {bm25_scores.max():.4f}")
        print(f"📊 BM25 - Score promedio: {bm25_scores.mean():.4f}")
        
        # 3. COMPARAR Y SELECCIONAR MEJOR MÉTODO
        print(f"\n⚖️ COMPARANDO MÉTODOS")
        print("-" * 40)
        
        # Normalizar scores BM25 para comparación
        bm25_normalized = bm25_scores / (bm25_scores.max() + 1e-8) if bm25_scores.max() > 0 else bm25_scores
        
        # Calcular métricas de calidad para cada método
        tfidf_top_scores = [tfidf_similarities[idx] for idx in tfidf_sorted_indices[:5]]
        bm25_top_scores = [bm25_normalized[idx] for idx in bm25_sorted_indices[:5]]
        
        tfidf_quality = np.mean(tfidf_top_scores) if tfidf_top_scores else 0
        bm25_quality = np.mean(bm25_top_scores) if bm25_top_scores else 0
        
        # Decidir qué método usar
        if tfidf_quality > bm25_quality:
            selected_method = "TF-IDF"
            selected_similarities = tfidf_similarities
            selected_indices = tfidf_sorted_indices
            reason = f"Mayor calidad promedio en top 5: {tfidf_quality:.4f} vs {bm25_quality:.4f}"
        else:
            selected_method = "BM25"
            selected_similarities = bm25_normalized
            selected_indices = bm25_sorted_indices
            reason = f"Mayor calidad promedio en top 5: {bm25_quality:.4f} vs {tfidf_quality:.4f}"
        
        print(f"🏆 Método seleccionado: {selected_method}")
        print(f"💡 Razón: {reason}")
        print(f"📊 TF-IDF calidad: {tfidf_quality:.4f}")
        print(f"📊 BM25 calidad: {bm25_quality:.4f}")
        
        # 4. GENERAR RESULTADOS CON EL MÉTODO SELECCIONADO
        print(f"\n🎯 GENERANDO RESULTADOS CON {selected_method}")
        print("-" * 40)
        
        results = []
        for idx in selected_indices:
            similarity_score = selected_similarities[idx]
            
            # Aplicar umbral
            if similarity_score < threshold:
                break
                
            doc = documents_data[idx].copy()
            doc['similarity_score'] = float(similarity_score)
            doc['rank'] = len(results) + 1
            doc['method_used'] = selected_method
            doc['method_reason'] = reason
            
            # Agregar scores de ambos métodos para comparación
            doc['tfidf_score'] = float(tfidf_similarities[idx])
            doc['bm25_score'] = float(bm25_scores[idx])
            doc['bm25_normalized'] = float(bm25_normalized[idx])
            
            # Preview del texto
            if 'text_original' in doc:
                doc['preview'] = doc['text_original'][:200] + "..." if len(doc['text_original']) > 200 else doc['text_original']
            
            results.append(doc)
            print(f"  ✅ Doc {idx}: {similarity_score:.4f} - {doc.get('title', f'Documento {idx}')[:50]}")
            
            if len(results) >= limit:
                break
        
        print(f"\n✅ RESUMEN FINAL HÍBRIDO:")
        print("-" * 40)
        print(f"🏆 Método usado: {selected_method}")
        print(f"💡 Razón: {reason}")
        print(f"📊 Resultados finales: {len(results)}")
        print(f"🎯 Umbral usado: {threshold}")
        print("="*60)
        
        return results
        
    except Exception as e:
        print(f"❌ Error en búsqueda híbrida: {e}")
        import traceback
        traceback.print_exc()
        return []

# Ruta básica para verificar que el servidor funciona
@app.route('/')
def home():
    status = "OK" if corpus_preprocesado is not None else "Preprocesamiento pendiente"
    return jsonify({
        "message": "Backend funcionando correctamente",
        "status": status,
        "documentos_preprocesados": len(corpus_preprocesado) if corpus_preprocesado is not None else 0,
        "matriz_tfidf": f"{tfidf_matrix.shape}" if tfidf_matrix is not None else "No creada",
        "vocabulario_size": len(vectorizer.vocabulary_) if vectorizer is not None else 0
    })

# Ruta para búsquedas por similitud coseno
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '').strip()
    limit = data.get('limit', 10)
    use_expansion = data.get('expansion', False)
    threshold = data.get('threshold', 0.1)
    
    if not query:
        return jsonify({
            "error": "Query vacía",
            "query": query
        }), 400
    
    if corpus_preprocesado is None or tfidf_matrix is None or bm25_model is None:
        return jsonify({
            "error": "Sistema no inicializado. Preprocesamiento pendiente.",
            "query": query
        }), 503
    
    start_time = time.time()
    
    try:
        # Usar búsqueda híbrida por defecto
        if use_expansion:
            results = busqueda_con_expansion_query(query, limit)
        else:
            results = busqueda_hibrida_tfidf_bm25(query, limit, threshold)
        
        search_time = time.time() - start_time
        
        # Extraer información del método usado
        method_used = "Híbrido (TF-IDF + BM25)"
        method_reason = ""
        if results:
            method_used = f"Híbrido: {results[0].get('method_used', 'Desconocido')}"
            method_reason = results[0].get('method_reason', '')
        
        return jsonify({
            "query": query,
            "results": results,
            "total": len(results),
            "corpus_size": len(corpus_preprocesado),
            "search_time": round(search_time, 3),
            "expansion_used": use_expansion,
            "threshold": threshold,
            "method_used": method_used,
            "method_reason": method_reason,
            "search_type": "hybrid_tfidf_bm25"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error en búsqueda: {str(e)}",
            "query": query
        }), 500

# Ruta para obtener documento específico
@app.route('/document/<int:doc_id>')
def get_document(doc_id):
    if corpus_preprocesado is None:
        return jsonify({"error": "Sistema no inicializado"}), 503
    
    if doc_id < 0 or doc_id >= len(documents_data):
        return jsonify({"error": "Documento no encontrado"}), 404
    
    return jsonify(documents_data[doc_id])

# Ruta para documentos similares a uno específico
@app.route('/similar/<int:doc_id>')
def find_similar_documents(doc_id):
    limit = request.args.get('limit', 5, type=int)
    
    if corpus_preprocesado is None or tfidf_matrix is None:
        return jsonify({"error": "Sistema no inicializado"}), 503
    
    if doc_id < 0 or doc_id >= len(documents_data):
        return jsonify({"error": "Documento no encontrado"}), 404
    
    try:
        # Obtener vector del documento
        doc_vector = tfidf_matrix[doc_id]
        
        # Calcular similitudes con todos los documentos
        similarities = cosine_similarity(doc_vector, tfidf_matrix).flatten()
        
        # Obtener índices ordenados (excluyendo el documento original)
        sorted_indices = np.argsort(similarities)[::-1]
        similar_docs = []
        
        for idx in sorted_indices:
            if idx != doc_id and similarities[idx] > 0.1:  # Excluir el mismo documento
                doc = documents_data[idx].copy()
                doc['similarity_score'] = float(similarities[idx])
                similar_docs.append(doc)
                
                if len(similar_docs) >= limit:
                    break
        
        return jsonify({
            "original_document": documents_data[doc_id],
            "similar_documents": similar_docs,
            "total": len(similar_docs)
        })
        
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

# Ruta para estadísticas del sistema
@app.route('/stats')
def get_stats():
    if corpus_preprocesado is None:
        return jsonify({"error": "Sistema no inicializado"}), 503
    
    return jsonify({
        "total_documents": len(corpus_preprocesado),
        "tfidf_matrix_shape": list(tfidf_matrix.shape) if tfidf_matrix is not None else None,
        "vocabulary_size": len(vectorizer.vocabulary_) if vectorizer is not None else 0,
        "system_status": "Operativo"
    })

if __name__ == '__main__':
    print("🚀 Iniciando sistema de recuperación de información...")
    
    # Ejecutar preprocesamiento antes de iniciar el servidor
    if inicializar_sistema():
        print("✅ Sistema listo con búsqueda por similitud coseno")
        print("🚀 Backend iniciando en http://localhost:3000")
        app.run(debug=True, host='0.0.0.0', port=3000)
    else:
        print("❌ Error: No se pudo inicializar el sistema")
        exit(1)