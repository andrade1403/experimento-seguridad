import logging
import requests
from rol import Rol
from flask_jwt_extended import get_jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from modelos import db, RequestService, Usuario

#Creamos app de flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbpeticiones.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app_context = app.app_context()
app_context.push()

#Inicializamos la base de datos
db.init_app(app)
db.create_all()

#Creamos los dos usuarios en base de datos
usuario_1 = Usuario(nombre = 'usuario1', contrasenia = 'pass1', rol = Rol.DIRECTOR)
usuario_2 = Usuario(nombre = 'usuario2', contrasenia = 'pass2', rol = Rol.OPERARIO)
db.session.add(usuario_1)
db.session.add(usuario_2)
db.session.commit()

#Ponemos rutas de microservicios
microservicios = {'login': 'http://localhost:5001',
                  'ventas': 'http://localhost:5002'}

#URL de la API de metricas
metrics_report_api = 'https://prevebsabackend.azurewebsites.net/api/RequestBlocks'

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
    #Definimos la hora hace dos minutos
    hora_dos_minutos = datetime.now() - timedelta(minutes = 2)

    #Contamos las peticiones del usuario
    contador = RequestService.query.filter(RequestService.usuario == usuario.nombre, RequestService.fecha_peticion >= hora_dos_minutos).count()

    return contador

@app.before_request
def bloqueoUsuario():
    #Definimos el umbral de peticiones
    umbral = 10

    #Extraemos el usuario del token
    userName = get_jwt().get('sub')

    #Traemos el usuarios de la base de datos
    usuario_db = Usuario.query.filter(Usuario.nombre == userName).first()

    #Peticion del request
    peticion = request.method

    #Validamos si el usuario esta bloqueado
    if usuario_db.estado is False:
        return jsonify({'mensaje': 'Usuario bloqueado'}), 204

    #Validamos la cantidad de request del usuario
    if conteoPeticiones(usuario_db) >= umbral:
        usuario_db.estado = False
        db.session.add(usuario_db)
        db.session.commit()
        metricas(usuario_db.id, peticion, 403, True)
        return jsonify({'mensaje': 'Usuario bloqueado por exceso de peticiones'}), 403
        
    #Creamos los datos para la persistencia
    request_service = RequestService(usuario = usuario_db.nombre)
    db.session.add(request_service)
    db.session.commit()
    metricas(usuario_db.id, peticion, 200, False)

#Bloqueamos el acceso a las rutas sin token
API_GATEWAY_KEY = "llavesecreta"

#Funcion para mandar solicitud a microservicio
def envioSolicitud(microservicio, ruta):
    try:
        #Validamos que el microservicio si exista
        if microservicio not in microservicios:
            return jsonify({"error": "Microservicio no reconocido"}), 400
        
        #Añadimos la API Key en el header
        headers = dict(request.headers)
        headers["X-API-KEY"] = API_GATEWAY_KEY
        headers["X-GATEWAY"] = "API_GATEWAY"

        #Traemos el microservicio por parametro
        url = f'{microservicios[microservicio]}{ruta}'

        #Tipo de peticion
        peticion = request.method

        #Enviamos solicitud
        response = requests.request(peticion, url, json = request.json, headers = headers)

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({'mensaje': 'Error al conectar con el microservicio'}), 500
 
#Rutas a los microservicios de ventas
@app.route('/ventas', methods = ['GET', 'POST'])
def ventas():
    return envioSolicitud('ventas', '/ventas')

#Rutas al componente de autorizador
@app.route('/login', methods = ['POST'])
def login():
    return envioSolicitud('login', '/login')