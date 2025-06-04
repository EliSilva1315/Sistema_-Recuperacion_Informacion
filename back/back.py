from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite conexiones desde tu frontend Angular

# Ruta básica para verificar que el servidor funciona
@app.route('/')
def home():
    return jsonify({
        "message": "Backend funcionando correctamente",
        "status": "OK"
    })

# Ruta para búsquedas
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '')
    
    # Por ahora devolvemos datos mock
    results = [
        {
            "title": f"Resultado para: {query}",
            "url": "https://example.com/1",
            "description": f"Este es un resultado de búsqueda para '{query}' desde el backend Python.",
            "featured": True
        },
        {
            "title": f"Segundo resultado para: {query}",
            "url": "https://example.com/2", 
            "description": f"Otro resultado relevante para tu búsqueda de '{query}'.",
            "featured": False
        }
    ]
    
    return jsonify({
        "query": query,
        "results": results,
        "total": len(results)
    })

if __name__ == '__main__':
    print("🚀 Backend iniciando en http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)