import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import json
from google.cloud import speech


API_KEY = os.environ['GEMINI_KEY']  # Clave API para Gemini
genai.configure(api_key=API_KEY)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

app = Flask(__name__)

API_KEY = os.environ['SECRETO']  # Clave API para la aplicación


# Función para verificar la clave API
def verify_api_key(api_key):
    if api_key != API_KEY:
        return jsonify({'message': 'Clave API inválida'}), 401

# Endpoint protegido que requiere la clave API
@app.route('/merca-ia-voice', methods=['POST'])
def read_voice():
    # Verifica la clave API en la cabecera de la solicitud
    api_key = request.headers.get('api_key')
    if not api_key:
        return jsonify({'message': 'Falta la clave API'}), 401

    response = verify_api_key(api_key)
    if response:
        return response

    # Obtiene el input del cuerpo de la solicitud
    try:
        data = request.get_json()
        input_text = data.get('input_text')

        credentials_json = os.environ['GOOGLE_KEY']  # Reemplaza con tu JSON
        credentials = json.loads(credentials_json)

        # Crea un cliente para la API de Speech-to-Text con las credenciales
        client = speech.SpeechClient(credentials=credentials)
        client = speech.SpeechClient()
        audio_bytes = base64.b64decode(input_text)

        # Crear un objeto RecognitionAudio a partir de los bytes del audio
        audio = speech.RecognitionAudio(content=audio_bytes)
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="es-ES",# Código de idioma español de España
        )
        
        # Realiza la solicitud de transcripción
        response = client.recognize(config=config, audio=audio)
        
        # Imprime los resultados
        for result in response.results:
            print("Transcripción: {}".format(result.alternatives[0].transcript))
        
        if not input_text:
            return jsonify({'message': 'Falta el texto de entrada'}), 400
    except:
        return jsonify({'message': 'Formato de entrada inválido'}), 400
        
    
    

# Endpoint protegido que requiere la clave API
@app.route('/merca-ia', methods=['POST'])
def read_items():
    # Verifica la clave API en la cabecera de la solicitud
    api_key = request.headers.get('api_key')
    if not api_key:
        return jsonify({'message': 'Falta la clave API'}), 401

    response = verify_api_key(api_key)
    if response:
        return response

    # Obtiene el input del cuerpo de la solicitud
    try:
        data = request.get_json()
        input_text = data.get('input_text')
        if not input_text:
            return jsonify({'message': 'Falta el texto de entrada'}), 400
    except:
        return jsonify({'message': 'Formato de entrada inválido'}), 400

    # Construye el prompt con el input_text
    prompt = f"""
    Extrae la siguiente información del texto proporcionado:

    * Fecha
    * Capacidad
    * Tipo de reunión
    * Tipo de comida (desayuno, almuerzo, comida)

    Texto: {input_text}

    Devuelve SOLO la información extraída en formato JSON, sin saltos de línea y sin incluir ningún campo adicional como "response":
    {{
      "fecha": "valor",
      "capacidad": "valor",
      "tipo_reunion": "valor",
      "tipo_comida": "valor"
    }}
    """

    # Pasa el prompt al modelo
    response = model.generate_content([prompt])

    # Extrae el texto de la respuesta
    response_text = response.text

    # Procesa la respuesta del modelo (aquí debes implementar la lógica para extraer el JSON)
    try:
        # Convierte la respuesta JSON en un diccionario (ajusta según el formato de tu respuesta)
        criterios_sala = json.loads(response_text)
        # ... usa los criterios_sala para construir el prompt de búsqueda ...
    except:
        return jsonify({'message': 'Error al procesar la respuesta del modelo'}), 500

    return jsonify({'response': response_text})  # Devuelve la respuesta del modelo


@app.route("/")
def hello_world():
    return render_template("index.html")
