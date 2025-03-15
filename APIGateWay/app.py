import logging
import requests
from flask_cors import CORS
from flask_jwt_extended import get_jwt, jwt_required, verify_jwt_in_request, JWTManager
from flask import Flask, request, jsonify

#Creamos app de flask
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "supersecretkey"
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
CORS(app)
app_context = app.app_context()
app_context.push()

#Inicializamos el JWTManager
jwt = JWTManager(app)

#Ponemos rutas de microservicios
microservicios = {'login': 'https://autorizador.mangomushroom-a6b9d05e.westus2.azurecontainerapps.io',
                  'inventarios': 'https://ms-inventarios.bluemoss-dcbfacb8.westus2.azurecontainerapps.io'}

#URL de la API de metricas
metrics_report_api = 'https://prevebsabackend.azurewebsites.net/api/RequestBlocks'

#Bloqueamos el acceso a las rutas sin token
API_GATEWAY_KEY = "llavesecreta"

def metricas(id, peticion, status_code, blocked):
    #Creamos el json con la informacion de la metrica
    json = {
        "UserId": id,
        "RequestType": peticion,
        "StatusCode": status_code,
        "Blocked": blocked
    }

    #Enviamos metricas a la URL de la API
    send_metrics(json)

def send_metrics(message_body):
    try:
        response = requests.post(metrics_report_api, json = message_body)
        logging.info(f"Metrics sent - Status: {response.status_code}")

    except Exception as e:
        logging.error(f"An error occurred while sending metrics: {e}")

def conteoPeticiones(usuario):
    # #Añadimos la API Key en el header
    # headers = dict(request.headers)
    # headers["X-API-KEY"] = API_GATEWAY_KEY
    # headers["X-GATEWAY"] = "API_GATEWAY"

    #Contamos las peticiones del usuario
    contador = requests.request('GET', f'https://autorizador.mangomushroom-a6b9d05e.westus2.azurecontainerapps.io/peticiones/{usuario}', json = request.json).json()

    return contador['contador']

@app.before_request
def bloqueoUsuario():
    if request.path == "/login":
        return
    
    # #Añadimos la API Key en el header
    # headers = dict(request.headers)
    # headers["X-API-KEY"] = API_GATEWAY_KEY
    # headers["X-GATEWAY"] = "API_GATEWAY"

    #Definimos el umbral de peticiones
    umbral = 8

    #Extraemos el nombre de usuario del token
    verify_jwt_in_request()
    jwt_data = get_jwt()
    userName = jwt_data['sub']

    #Peticion del request
    peticion = request.method

    #Definimos la URL de la API de usuarios
    url = f'https://autorizador.mangomushroom-a6b9d05e.westus2.azurecontainerapps.io/usuarios/{userName}'

    #Traemos el usuario de la base de datos
    usuario_db = requests.request('GET', url, json = request.json).json()

    #Validamos si el usuario esta bloqueado
    if usuario_db['estado'] is False:
        return jsonify({'mensaje': 'Usuario bloqueado'}), 403

    #Validamos la cantidad de request del usuario
    if conteoPeticiones(usuario_db['nombre']) >= umbral:
        usuario_actualizado = requests.request('PUT', url, json = request.json).json()
        metricas(usuario_actualizado['nombre'], peticion, 403, True)
        return jsonify({'mensaje': 'Usuario bloqueado por exceso de peticiones'}), 403
        
    #Creamos los datos para la persistencia
    request_service = requests.request('POST', 'https://autorizador.mangomushroom-a6b9d05e.westus2.azurecontainerapps.io/peticiones', json = request.json)

#Funcion para mandar solicitud a microservicio
def envioSolicitud(microservicio, ruta):
    try:
        #Validamos que el microservicio si exista
        if microservicio not in microservicios:
            return jsonify({"error": "Microservicio no reconocido"}), 400
        
        # #Añadimos la API Key en el header
        # headers = dict(request.headers)
        # headers["X-API-KEY"] = API_GATEWAY_KEY
        # headers["X-GATEWAY"] = "API_GATEWAY"

        #Traemos el microservicio por parametro
        url = f'{microservicios[microservicio]}{ruta}'

        #Tipo de peticion
        peticion = request.method

        #Enviamos solicitud
        response = requests.request(peticion, url, json = request.json)
        print(response.json())
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        print(e)
        return jsonify({'mensaje': 'Error al conectar con el microservicio'}), 500

#Rutas al micorservicio de inventarios
@app.route('/inventarios', methods = ['GET'])
@jwt_required()
def inventarios():
    return envioSolicitud('inventarios', '/inventarios')

@app.route('/entradaAleatoria', methods = ['POST'])
@jwt_required()
def entradaAleatoria():
    return envioSolicitud('inventarios', '/entradaAleatoria')

@app.route('/salidaAleatoria', methods = ['PUT'])
@jwt_required()
def salidaAleatoria():
    return envioSolicitud('inventarios', '/salidaAleatoria')

#Rutas al componente de autorizador
@app.route('/login', methods = ['POST'])
def login():
    return envioSolicitud('login', '/login')