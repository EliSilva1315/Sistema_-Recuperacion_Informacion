import pandas as pd
import json
import re
from collections import defaultdict
from back import busqueda_por_similitud_coseno, inicializar_sistema
from datetime import datetime

# Inicializar el sistema de recuperación
def main():
    inicializar_sistema()
    
    # Preguntar al usuario si solo quiere guardar la tabla
    save_only_table = input("¿Quieres guardar solo la tabla? (y/n): ").strip().lower() == 'y'
    
    # Crear archivo para análisis de resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_file = f"evaluacion_resultados_{timestamp}.txt"
    
    # Procesar todos los datos igual que antes
    
    # Leer qrels
    qrels = pd.read_csv('gaming/qrels/test.tsv', sep='\t')
    qrels.columns = ['query_id', 'doc_id', 'score']
    
    # Agrupar documentos relevantes por query
    relevant_docs = qrels[qrels['score'] > 0].groupby('query_id')['doc_id'].apply(set).to_dict()
    
    # Leer corpus y crear múltiples mapeos para identificar documentos
    corpus = {}
    corpus_id_map = {}
    corpus_title_map = {}
    
    with open('gaming/corpus.jsonl', 'r') as corpus_file:
        for line in corpus_file:
            doc = json.loads(line)
            corpus_id = str(doc['_id'])
            
            # Almacenar el documento por su ID original
            corpus[corpus_id] = doc
            
            # Crear mapeos adicionales para facilitar coincidencias
            title = doc.get('title', '').lower()
            if title:
                corpus_title_map[title] = corpus_id
            
            # Crear entradas para diferentes formatos de IDs
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
    
    # Si alguna query_id relevante no está en queries_text, buscar alternativas
    for qid in relevant_docs.keys():
        if str(qid) not in queries_text:
            if str(qid) in corpus:
                queries_text[str(qid)] = corpus[str(qid)]['title']
    
    # Procesar cada query y buscar documentos relevantes
    precisions = []
    recalls = []
    average_precisions = []
    consultas_validas = 0
    
    # Detalles por query
    query_details = []
    
    for qid in relevant_docs:
        # Obtener el texto de la query
        query_text = queries_text.get(str(qid), '')
        if not query_text:
            continue
        
        # Obtener los IDs de corpus para los documentos relevantes
        relevant_corpus_ids = set()
        for doc_id in relevant_docs[qid]:
            doc_id_str = str(doc_id)
            
            # Intentar diferentes formatos para encontrar el ID del corpus
            if doc_id_str in corpus:
                relevant_corpus_ids.add(doc_id_str)
            elif doc_id_str in corpus_id_map:
                mapped_id = corpus_id_map[doc_id_str]
                relevant_corpus_ids.add(mapped_id)
            elif "corpus-" in doc_id_str:
                # Si es formato "corpus-ID", extraer el ID
                pure_id = doc_id_str.split("-", 1)[1]
                if pure_id in corpus:
                    relevant_corpus_ids.add(pure_id)
        
        # Realizar la búsqueda
        retrieved = busqueda_por_similitud_coseno(query_text, limit=20)
        
        if not retrieved or not isinstance(retrieved, list):
            continue
            
        # Extraer IDs de los resultados
        retrieved_ids = []
        retrieved_positions = {}
        
        for i, doc in enumerate(retrieved):
            if not isinstance(doc, dict) or 'id' not in doc:
                continue
                
            doc_id = str(doc['id'])
            retrieved_ids.append(doc_id)
            retrieved_positions[doc_id] = i + 1
        
        # Encontrar coincidencias entre resultados y documentos relevantes
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
        
        precisions.append(precision)
        recalls.append(recall)
        
        # Average Precision
        if positions:
            positions.sort()  # Ordenar por posición
            sum_precisions = sum((i+1) / pos for i, pos in enumerate(positions))
            ap = sum_precisions / len(relevant_docs[qid])
        else:
            ap = 0
            
        average_precisions.append(ap)
        consultas_validas += 1
        
        # Guardar datos para la tabla resumen
        query_details.append({
            'qid': qid,
            'precision': precision,
            'recall': recall,
            'ap': ap,
            'relevantes': len(relevant_docs[qid]),
            'recuperados': len(retrieved_ids),
            'coincidencias': len(matches)
        })
    
    # Calcular MAP
    MAP = sum(average_precisions) / consultas_validas if consultas_validas > 0 else 0
    
    # Ahora escribir al archivo según la preferencia del usuario
    with open(analysis_file, 'w', encoding='utf-8') as f:
        if not save_only_table:
            # Escribir el análisis completo
            f.write("=======================================================\n")
            f.write("ANÁLISIS DE EVALUACIÓN DEL SISTEMA DE RECUPERACIÓN\n")
            f.write(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=======================================================\n\n")
            
            # Imprimir ejemplos del archivo qrels para depuración
            f.write("Primeras 5 filas del archivo qrels:\n")
            f.write(qrels.head().to_string() + "\n\n")
            
            f.write(f"Total de queries en qrels: {len(relevant_docs)}\n")
            
            # Imprimir algunos ejemplos de mapeos para depuración
            f.write("\nEjemplos de mapeos de IDs en el corpus:\n")
            count = 0
            for k, v in corpus_id_map.items():
                if k != v:  # Solo mostrar mapeos diferentes
                    f.write(f"  {k} -> {v}\n")
                    count += 1
                    if count >= 5:
                        break
            
            # Verificar manualmente si los documentos relevantes existen en el corpus
            f.write("\nVerificando existencia de documentos relevantes:\n")
            for qid, docs in list(relevant_docs.items())[:5]:  # Mostrar solo las primeras 5 queries
                f.write(f"\nQuery {qid}:\n")
                for doc_id in list(docs)[:3]:  # Mostrar solo los primeros 3 docs relevantes
                    doc_id_str = str(doc_id)
                    exists = False
                    corpus_doc_id = None
                    
                    # Comprobar diferentes formatos
                    if doc_id_str in corpus:
                        exists = True
                        corpus_doc_id = doc_id_str
                    elif doc_id_str in corpus_id_map:
                        exists = True
                        corpus_doc_id = corpus_id_map[doc_id_str]
                    
                    status = "✅ EXISTE" if exists else "❌ NO EXISTE"
                    f.write(f"  Doc {doc_id_str}: {status}\n")
                    
                    if exists and corpus_doc_id in corpus:
                        title = corpus[corpus_doc_id].get('title', '')
                        f.write(f"    Título: {title}\n")
            
            f.write("\n\n=======================================================\n")
            f.write("RESULTADOS DETALLADOS POR QUERY\n")
            f.write("=======================================================\n\n")
            
            for qid in relevant_docs:
                query_text = queries_text.get(str(qid), '')
                if not query_text:
                    continue
                
                f.write(f"\n\n-------------------------------------------------------\n")
                f.write(f"ANÁLISIS DE QUERY: {qid}\n")
                f.write(f"-------------------------------------------------------\n")
                f.write(f"Texto de query: {query_text}\n\n")
                
                # Obtener los IDs de corpus para los documentos relevantes
                relevant_corpus_ids = set()
                f.write("Documentos relevantes:\n")
                for doc_id in relevant_docs[qid]:
                    doc_id_str = str(doc_id)
                    f.write(f"  - Original: {doc_id_str}")
                    
                    # Intentar diferentes formatos para encontrar el ID del corpus
                    if doc_id_str in corpus:
                        relevant_corpus_ids.add(doc_id_str)
                        title = corpus[doc_id_str].get('title', '')
                        f.write(f" → Encontrado como: {doc_id_str} - {title}\n")
                    elif doc_id_str in corpus_id_map:
                        mapped_id = corpus_id_map[doc_id_str]
                        relevant_corpus_ids.add(mapped_id)
                        title = corpus[mapped_id].get('title', '')
                        f.write(f" → Encontrado como: {mapped_id} - {title}\n")
                    elif "corpus-" in doc_id_str:
                        # Si es formato "corpus-ID", extraer el ID
                        pure_id = doc_id_str.split("-", 1)[1]
                        if pure_id in corpus:
                            relevant_corpus_ids.add(pure_id)
                            title = corpus[pure_id].get('title', '')
                            f.write(f" → Encontrado como: {pure_id} - {title}\n")
                    else:
                        f.write(" ❌ No encontrado en corpus\n")
                
                f.write(f"\nIDs de corpus relevantes: {relevant_corpus_ids}\n")
                
                # Realizar la búsqueda
                retrieved = busqueda_por_similitud_coseno(query_text, limit=20)
                
                if not retrieved:
                    f.write(f"\n[WARN] No se encontraron resultados para la query '{query_text}'\n")
                    continue
                    
                if not isinstance(retrieved, list):
                    f.write(f"\n[ERROR] El resultado de busqueda_por_similitud_coseno no es una lista: {type(retrieved)}\n")
                    continue
                    
                # Extraer IDs de los resultados
                retrieved_ids = []
                retrieved_positions = {}
                
                f.write("\nDocumentos recuperados:\n")
                for i, doc in enumerate(retrieved):
                    if not isinstance(doc, dict):
                        f.write(f"[ERROR] Documento recuperado no es un diccionario: {type(doc)}\n")
                        continue
                        
                    if 'id' not in doc:
                        f.write(f"[ERROR] Documento recuperado no tiene campo 'id': {doc.keys()}\n")
                        continue
                        
                    doc_id = str(doc['id'])
                    retrieved_ids.append(doc_id)
                    retrieved_positions[doc_id] = i + 1
                    
                    f.write(f"  - #{i+1}: ID={doc_id}, Título={doc.get('title', '')[:50]}\n")
                
                # Encontrar coincidencias entre resultados y documentos relevantes
                matches = set()
                positions = []
                
                f.write("\nCoincidencias por ID:\n")
                for ret_id in retrieved_ids:
                    if ret_id in relevant_corpus_ids:
                        matches.add(ret_id)
                        positions.append(retrieved_positions[ret_id])
                        f.write(f"  ✅ Coincidencia: {ret_id} en posición {retrieved_positions[ret_id]}\n")
                
                # Si no hay coincidencias por ID, intentar por título
                if not matches:
                    f.write("\nIntentando coincidencias por título...\n")
                    for doc in retrieved:
                        title = doc.get('title', '').lower()
                        if title and title in corpus_title_map:
                            corpus_id = corpus_title_map[title]
                            if corpus_id in relevant_corpus_ids:
                                doc_id = str(doc['id'])
                                matches.add(doc_id)
                                positions.append(retrieved_positions[doc_id])
                                f.write(f"  ✅ Coincidencia por título: {doc_id}\n")
                
                f.write(f"\nCoincidencias totales encontradas: {len(matches)}\n")
                
                # Calcular métricas
                true_positives = len(matches)
                precision = true_positives / len(retrieved_ids) if retrieved_ids else 0
                recall = true_positives / len(relevant_docs[qid]) if relevant_docs[qid] else 0
                
                precisions.append(precision)
                recalls.append(recall)
                
                # Average Precision
                if positions:
                    positions.sort()  # Ordenar por posición
                    sum_precisions = sum((i+1) / pos for i, pos in enumerate(positions))
                    ap = sum_precisions / len(relevant_docs[qid])
                else:
                    ap = 0
                    
                average_precisions.append(ap)
                consultas_validas += 1
                
                f.write(f"\nMÉTRICAS:\n")
                f.write(f"  - Precision: {precision:.4f}\n")
                f.write(f"  - Recall: {recall:.4f}\n")
                f.write(f"  - AP: {ap:.4f}\n")
                
                # Guardar datos para la tabla resumen
                query_details.append({
                    'qid': qid,
                    'precision': precision,
                    'recall': recall,
                    'ap': ap,
                    'relevantes': len(relevant_docs[qid]),
                    'recuperados': len(retrieved_ids),
                    'coincidencias': len(matches)
                })
        
        # Siempre escribir la tabla resumen de resultados
        f.write("\n\n=======================================================\n")
        f.write("TABLA RESUMEN DE RESULTADOS\n")
        f.write("=======================================================\n\n")
        f.write(f"{'Query ID':<10} | {'Precision':<10} | {'Recall':<10} | {'AP':<10} | {'Relevantes':<10} | {'Recuperados':<12} | {'Coincidencias':<12}\n")
        f.write(f"{'-'*10:<10} | {'-'*10:<10} | {'-'*10:<10} | {'-'*10:<10} | {'-'*10:<10} | {'-'*12:<12} | {'-'*12:<12}\n")

        for detail in query_details:
            f.write(f"{detail['qid']:<10} | {detail['precision']:.4f}{' '*5} | {detail['recall']:.4f}{' '*5} | {detail['ap']:.4f}{' '*5} | {detail['relevantes']:<10} | {detail['recuperados']:<12} | {detail['coincidencias']:<12}\n")

        if consultas_validas == 0:
            f.write("\nNo se encontró ninguna consulta válida para evaluar.\n")
        else:
            # Resultados finales - siempre incluir
            f.write("\n\n=======================================================\n")
            f.write("RESULTADOS FINALES\n")
            f.write("=======================================================\n\n")
            f.write(f"Precision promedio: {sum(precisions)/consultas_validas:.4f}\n")
            f.write(f"Recall promedio: {sum(recalls)/consultas_validas:.4f}\n")
            f.write(f"MAP: {MAP:.4f}\n\n")

        if not save_only_table:
            # Análisis de resultados
            f.write("=======================================================\n")
            f.write("ANÁLISIS DE RESULTADOS\n")
            f.write("=======================================================\n\n")

            # Analysis of best and worst performing queries
            if query_details:
                query_details.sort(key=lambda x: x['ap'], reverse=True)
                
                f.write("Top 5 consultas con mejor desempeño:\n")
                for i, detail in enumerate(query_details[:5]):
                    f.write(f"  {i+1}. Query {detail['qid']}: AP={detail['ap']:.4f}, Precision={detail['precision']:.4f}, Recall={detail['recall']:.4f}\n")
                    f.write(f"     Texto: {queries_text.get(str(detail['qid']), 'N/A')[:100]}\n\n")
                
                f.write("\n5 consultas con peor desempeño:\n")
                for i, detail in enumerate(query_details[-5:]):
                    f.write(f"  {i+1}. Query {detail['qid']}: AP={detail['ap']:.4f}, Precision={detail['precision']:.4f}, Recall={detail['recall']:.4f}\n")
                    f.write(f"     Texto: {queries_text.get(str(detail['qid']), 'N/A')[:100]}\n\n")

            f.write("\n=======================================================\n")
            f.write("FIN DEL ANÁLISIS\n")
            f.write("=======================================================\n")
    
    print(f"\nRESULTADOS FINALES:")
    print(f"Precision promedio: {sum(precisions)/consultas_validas:.4f}")
    print(f"Recall promedio: {sum(recalls)/consultas_validas:.4f}")
    print(f"MAP: {MAP:.4f}")
    print(f"\nEl análisis {'resumido' if save_only_table else 'completo'} se ha guardado en: {analysis_file}")

if __name__ == '__main__':
    main()
