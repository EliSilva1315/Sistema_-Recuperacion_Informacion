from flask import Flask, jsonify, request
from flask_cors import CORS
from preprocesamiento import preprocesar_texto

app = Flask(__name__)
CORS(app)  # Permite conexiones desde tu frontend Angular

# Variable global para almacenar el corpus preprocesado
corpus_preprocesado = None

def inicializar_sistema():
    """Inicializa el sistema preprocesando el corpus"""
    global corpus_preprocesado
    print("🔄 Iniciando preprocesamiento del corpus...")
    try:
        corpus_preprocesado = preprocesar_texto()
        print("✅ Preprocesamiento completado exitosamente")
        print(f"📊 Documentos procesados: {len(corpus_preprocesado)}")
        return True
    except Exception as e:
        print(f"❌ Error en el preprocesamiento: {e}")
        return False

# Ruta básica para verificar que el servidor funciona
@app.route('/')
def home():
    status = "OK" if corpus_preprocesado is not None else "Preprocesamiento pendiente"
    return jsonify({
        "message": "Backend funcionando correctamente",
        "status": status,
        "documentos_preprocesados": len(corpus_preprocesado) if corpus_preprocesado is not None else 0
    })

# Ruta para búsquedas
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '')
    
    if corpus_preprocesado is None:
        return jsonify({
            "error": "Sistema no inicializado. Preprocesamiento pendiente.",
            "query": query
        }), 503
    
    # Por ahora devolvemos datos mock, pero ya tenemos acceso al corpus preprocesado
    results = [
        {
            "title": f"Resultado para: {query}",
            "url": "https://example.com/1",
            "description": f"Este es un resultado de búsqueda para '{query}' desde el backend Python con corpus preprocesado.",
            "featured": True
        },
        {
            "title": f"Segundo resultado para: {query}",
            "url": "https://example.com/2", 
            "description": f"Otro resultado relevante para tu búsqueda de '{query}' usando {len(corpus_preprocesado)} documentos.",
            "featured": False
        }
    ]
    
    return jsonify({
        "query": query,
        "results": results,
        "total": len(results),
        "corpus_size": len(corpus_preprocesado)
    })

if __name__ == '__main__':
    print("🚀 Iniciando sistema de recuperación de información...")
    
    # Ejecutar preprocesamiento antes de iniciar el servidor
    if inicializar_sistema():
        print("✅ Preprocesamiento listo")
        print("🚀 Backend iniciando en http://localhost:3000")
        app.run(debug=True, host='0.0.0.0', port=3000)
    else:
        print("❌ Error: No se pudo inicializar el sistema")
        exit(1)