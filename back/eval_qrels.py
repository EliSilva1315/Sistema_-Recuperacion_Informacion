import pandas as pd
import json
import re
from collections import defaultdict
from back import busqueda_por_similitud_coseno, inicializar_sistema
from datetime import datetime
import random
import os

# Inicializar el sistema de recuperación
def main():
    inicializar_sistema()
    
    # Preguntar al usuario si solo quiere guardar la tabla
    save_only_table = input("¿Quieres guardar solo la tabla? (y/n): ").strip().lower() == 'y'
    
    # Crear archivo para análisis de resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_file = f"evaluacion_resultados_{timestamp}.txt"
    
    # Leer qrels
    qrels = pd.read_csv('gaming/qrels/test.tsv', sep='\t')
    qrels.columns = ['query_id', 'doc_id', 'score']
    
    # Agrupar documentos relevantes por query
    relevant_docs = qrels[qrels['score'] > 0].groupby('query_id')['doc_id'].apply(set).to_dict()
    
    # Leer corpus y crear mapeos para identificar documentos
    corpus = {}
    corpus_id_map = {}
    corpus_title_map = {}
    
    with open('gaming/corpus.jsonl', 'r') as corpus_file:
        for line in corpus_file:
            doc = json.loads(line)
            corpus_id = str(doc['_id'])
            
            # Almacenar el documento y crear mapeos
            corpus[corpus_id] = doc
            
            title = doc.get('title', '').lower()
            if title:
                corpus_title_map[title] = corpus_id
            
            corpus_id_map[corpus_id] = corpus_id
            corpus_id_map[f"corpus-{corpus_id}"] = corpus_id
            corpus_id_map[corpus_id.lstrip('0')] = corpus_id
    
    # Leer queries.jsonl para obtener los textos de las queries
    queries_text = {}
    with open('/Users/eliasbolanos/Documents/querys/queries.jsonl', 'r') as queries_file:
        for line in queries_file:
            obj = json.loads(line)
            qid = str(obj.get('id') or obj.get('query_id') or obj.get('_id'))
            text = obj.get('text') or obj.get('query') or obj.get('title')
            if qid and text:
                queries_text[qid] = text
    
    # Completar queries faltantes con información del corpus
    for qid in relevant_docs.keys():
        if str(qid) not in queries_text and str(qid) in corpus:
            queries_text[str(qid)] = corpus[str(qid)]['title']
    
    # Variables para métricas
    precisions = []
    recalls = []
    average_precisions = []
    consultas_validas = 0
    query_details = []
    
    # Procesar cada query y evaluar resultados
    for qid in relevant_docs:
        # Obtener texto de query
        query_text = queries_text.get(str(qid), '')
        if not query_text:
            continue
        
        # Obtener IDs de documentos relevantes
        relevant_corpus_ids = set()
        for doc_id in relevant_docs[qid]:
            doc_id_str = str(doc_id)
            
            if doc_id_str in corpus:
                relevant_corpus_ids.add(doc_id_str)
            elif doc_id_str in corpus_id_map:
                relevant_corpus_ids.add(corpus_id_map[doc_id_str])
            elif "corpus-" in doc_id_str:
                pure_id = doc_id_str.split("-", 1)[1]
                if pure_id in corpus:
                    relevant_corpus_ids.add(pure_id)
        
        # Realizar búsqueda
        retrieved = busqueda_por_similitud_coseno(query_text, limit=20)
        
        if not retrieved or not isinstance(retrieved, list):
            continue
            
        # Extraer IDs de resultados
        retrieved_ids = []
        retrieved_positions = {}
        
        for i, doc in enumerate(retrieved):
            if not isinstance(doc, dict) or 'id' not in doc:
                continue
                
            doc_id = str(doc['id'])
            retrieved_ids.append(doc_id)
            retrieved_positions[doc_id] = i + 1
        
        # Encontrar coincidencias
        matches = set()
        positions = []
        
        for ret_id in retrieved_ids:
            if ret_id in relevant_corpus_ids:
                matches.add(ret_id)
                positions.append(retrieved_positions[ret_id])
        
        # Si no hay coincidencias por ID, intentar por título
        if not matches:
            for doc in retrieved:
                title = doc.get('title', '').lower()
                if title and title in corpus_title_map:
                    corpus_id = corpus_title_map[title]
                    if corpus_id in relevant_corpus_ids:
                        doc_id = str(doc['id'])
                        matches.add(doc_id)
                        positions.append(retrieved_positions[doc_id])
        
        # Calcular métricas
        true_positives = len(matches)
        precision = true_positives / len(retrieved_ids) if retrieved_ids else 0
        recall = true_positives / len(relevant_docs[qid]) if relevant_docs[qid] else 0
        
        # Average Precision
        ap = 0
        if positions:
            positions.sort()
            sum_precisions = sum((i+1) / pos for i, pos in enumerate(positions))
            ap = sum_precisions / len(relevant_docs[qid])
            
        # Guardar métricas
        precisions.append(precision)
        recalls.append(recall)
        average_precisions.append(ap)
        consultas_validas += 1
        
        # Guardar datos para tabla resumen y los documentos recuperados
        query_details.append({
            'qid': qid,
            'precision': precision,
            'recall': recall,
            'ap': ap,
            'relevantes': len(relevant_docs[qid]),
            'recuperados': len(retrieved_ids),
            'coincidencias': len(matches),
            'query_text': query_text,
            'relevant_ids': relevant_corpus_ids,
            'matches': matches,
            'positions': positions,
            'retrieved_docs': retrieved[:5]  # Guardar los primeros 5 documentos recuperados
        })
    
    # Calcular MAP
    MAP = sum(average_precisions) / consultas_validas if consultas_validas > 0 else 0
    
    # Escribir resultados al archivo
    with open(analysis_file, 'w', encoding='utf-8') as f:
        if not save_only_table:
            # Escribir análisis completo
            f.write("=======================================================\n")
            f.write("ANÁLISIS DE EVALUACIÓN DEL SISTEMA DE RECUPERACIÓN\n")
            f.write(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=======================================================\n\n")
            
            f.write(f"Total de queries en qrels: {len(relevant_docs)}\n")
            f.write(f"Queries válidas procesadas: {consultas_validas}\n\n")
            
            # Resultados detallados por query
            f.write("\n=======================================================\n")
            f.write("RESULTADOS DETALLADOS POR QUERY\n")
            f.write("=======================================================\n\n")
            
            for detail in query_details:
                qid = detail['qid']
                f.write(f"\n-------------------------------------------------------\n")
                f.write(f"ANÁLISIS DE QUERY: {qid}\n")
                f.write(f"-------------------------------------------------------\n")
                f.write(f"Texto de query: {detail['query_text']}\n\n")
                
                f.write(f"Documentos relevantes: {detail['relevantes']}\n")
                f.write(f"Documentos recuperados: {detail['recuperados']}\n")
                f.write(f"Coincidencias encontradas: {detail['coincidencias']}\n\n")
                
                f.write(f"MÉTRICAS:\n")
                f.write(f"  - Precision: {detail['precision']:.4f}\n")
                f.write(f"  - Recall: {detail['recall']:.4f}\n")
                f.write(f"  - AP: {detail['ap']:.4f}\n")
        
        # Siempre escribir tabla resumen
        f.write("\n\n=======================================================\n")
        f.write("TABLA RESUMEN DE RESULTADOS\n")
        f.write("=======================================================\n\n")
        f.write(f"{'Query ID':<10} | {'Precision':<10} | {'Recall':<10} | {'AP':<10} | {'Relevantes':<10} | {'Recuperados':<12} | {'Coincidencias':<12}\n")
        f.write(f"{'-'*10:<10} | {'-'*10:<10} | {'-'*10:<10} | {'-'*10:<10} | {'-'*10:<10} | {'-'*12:<12} | {'-'*12:<12}\n")

        for detail in query_details:
            f.write(f"{detail['qid']:<10} | {detail['precision']:.4f}{' '*5} | {detail['recall']:.4f}{' '*5} | {detail['ap']:.4f}{' '*5} | {detail['relevantes']:<10} | {detail['recuperados']:<12} | {detail['coincidencias']:<12}\n")

        # Resultados finales - siempre incluir
        f.write("\n\n=======================================================\n")
        f.write("RESULTADOS FINALES\n")
        f.write("=======================================================\n\n")
        f.write(f"Precision promedio: {sum(precisions)/consultas_validas:.4f}\n")
        f.write(f"Recall promedio: {sum(recalls)/consultas_validas:.4f}\n")
        f.write(f"MAP: {MAP:.4f}\n\n")

        # Siempre incluir 10 ejemplos de consultas y sus resultados
        f.write("\n=======================================================\n")
        f.write("EJEMPLOS DE CONSULTAS Y SUS RESULTADOS\n")
        f.write("=======================================================\n\n")
        
        # Seleccionar 10 ejemplos: 5 mejores y 5 aleatorios (o peores si hay suficientes)
        if query_details:
            # Ordenar por AP descendente
            sorted_details = sorted(query_details, key=lambda x: x['ap'], reverse=True)
            
            # Tomar los 5 mejores
            best_examples = sorted_details[:5]
            
            # Para los 5 restantes, si hay más de 10 ejemplos, tomar una mezcla de medios y peores
            remaining_examples = []
            if len(sorted_details) > 10:
                # Tomar 2 ejemplos de rendimiento medio y 3 peores
                middle_start = len(sorted_details) // 2 - 1
                remaining_examples = sorted_details[middle_start:middle_start+2] + sorted_details[-3:]
            else:
                # Si no hay suficientes, tomar los restantes
                remaining_examples = sorted_details[5:10]
            
            # Combinar en una lista de hasta 10 ejemplos
            examples = best_examples + remaining_examples
            examples = examples[:10]  # Asegurar máximo 10 ejemplos
            
            # Mostrar los ejemplos
            for i, detail in enumerate(examples):
                qid = detail['qid']
                f.write(f"\n-------------------------------------------------------\n")
                f.write(f"EJEMPLO {i+1}: QUERY {qid}\n")
                f.write(f"-------------------------------------------------------\n")
                f.write(f"Texto de query: {detail['query_text']}\n\n")
                
                f.write(f"MÉTRICAS: Precision={detail['precision']:.4f}, Recall={detail['recall']:.4f}, AP={detail['ap']:.4f}\n\n")
                
                f.write("TOP 5 DOCUMENTOS RECUPERADOS:\n")
                for j, doc in enumerate(detail['retrieved_docs'][:5]):
                    title = doc.get('title', 'Sin título')
                    doc_id = doc.get('id', 'ID desconocido')
                    is_relevant = "✓ RELEVANTE" if str(doc_id) in detail['matches'] else "✗ NO RELEVANTE"
                    
                    f.write(f"  {j+1}. [{is_relevant}] {title}\n")
                    if 'snippet' in doc:
                        snippet = doc['snippet']
                        if len(snippet) > 150:
                            snippet = snippet[:147] + "..."
                        f.write(f"     {snippet}\n")
                f.write("\n")

        if not save_only_table:
            # Análisis de resultados
            f.write("=======================================================\n")
            f.write("ANÁLISIS DE RESULTADOS\n")
            f.write("=======================================================\n\n")

            # Analysis of best and worst performing queries
            if query_details:
                sorted_details = sorted(query_details, key=lambda x: x['ap'], reverse=True)
                
                f.write("Top 5 consultas con mejor desempeño:\n")
                for i, detail in enumerate(sorted_details[:5]):
                    f.write(f"  {i+1}. Query {detail['qid']}: AP={detail['ap']:.4f}, Precision={detail['precision']:.4f}, Recall={detail['recall']:.4f}\n")
                    f.write(f"     Texto: {detail['query_text'][:100]}\n\n")
                
                f.write("\n5 consultas con peor desempeño:\n")
                for i, detail in enumerate(sorted_details[-5:]):
                    f.write(f"  {i+1}. Query {detail['qid']}: AP={detail['ap']:.4f}, Precision={detail['precision']:.4f}, Recall={detail['recall']:.4f}\n")
                    f.write(f"     Texto: {detail['query_text'][:100]}\n\n")

            f.write("\n=======================================================\n")
            f.write("FIN DEL ANÁLISIS\n")
            f.write("=======================================================\n")
    
    print(f"\nRESULTADOS FINALES:")
    print(f"Precision promedio: {sum(precisions)/consultas_validas:.4f}")
    print(f"Recall promedio: {sum(recalls)/consultas_validas:.4f}")
    print(f"MAP: {MAP:.4f}")
    print(f"\nEl análisis {'resumido con ejemplos' if save_only_table else 'completo'} se ha guardado en: {analysis_file}")

def mostrar_queries(ruta_archivo='/Users/eliasbolanos/Documents/querys/queries.jsonl'):
    """
    Muestra el contenido del archivo de queries en formato legible
    """
    if not os.path.exists(ruta_archivo):
        print(f"❌ No se encontró el archivo: {ruta_archivo}")
        return
    
    print(f"\n📋 CONTENIDO DE QUERIES.JSONL:")
    print("=" * 80)
    
    try:
        # Contar número total de queries
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            total_queries = sum(1 for _ in file)
        
        # Leer y mostrar el contenido
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            for i, line in enumerate(file, 1):
                try:
                    query = json.loads(line)
                    query_id = query.get('id') or query.get('query_id') or query.get('_id', f"query_{i}")
                    query_text = query.get('text') or query.get('query') or query.get('title', 'Sin texto')
                    
                    print(f"\n📌 QUERY {i}/{total_queries} - ID: {query_id}")
                    print(f"└─ {query_text}")
                except json.JSONDecodeError:
                    print(f"\n⚠️ Error al decodificar la línea {i}: {line[:100]}...")
        
        print("\n" + "=" * 80)
        print(f"✅ Total de queries: {total_queries}")
        
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")

if __name__ == '__main__':
    # Preguntar al usuario qué acción realizar
    print("\n🔍 SISTEMA DE EVALUACIÓN DE RECUPERACIÓN DE INFORMACIÓN")
    print("=" * 60)
    print("1. Ver queries.jsonl")
    print("2. Ejecutar evaluación")
    print("3. Salir")
    
    opcion = input("\nSelecciona una opción (1-3): ").strip()
    
    if opcion == '1':
        ruta = input("Introduce la ruta del archivo queries.jsonl (o presiona Enter para usar la predeterminada): ")
        if not ruta.strip():
            ruta = '/Users/eliasbolanos/Documents/querys/queries.jsonl'
        mostrar_queries(ruta)
        exit()
    elif opcion == '2':
        main()
    elif opcion == '3':
        print("Saliendo del programa...")
        exit()
    else:
        print("Opción no válida. Saliendo...")
        exit()
