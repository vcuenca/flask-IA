import os
from flask import Flask,request, jsonify, render_template

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("index.html")

API_KEY = os.environ['SECRETO']

# Función para verificar la clave API
def verify_api_key(api_key):
    if api_key != API_KEY:
        return jsonify({'message': 'Clave API inválida'}), 401

# Endpoint protegido que requiere la clave API
@app.route('/items', methods=['POST'])
def read_items():
    # Verifica la clave API en la cabecera de la solicitud
    api_key = request.headers.get('api_key')
    if not api_key:
        return jsonify({'message': 'Falta la clave API'}), 401

    response = verify_api_key(api_key)
    if response:
        return response

    return jsonify({'items': ['Item 1', 'Item 2']})
