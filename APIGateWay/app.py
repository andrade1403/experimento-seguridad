import requests
from modelos import db, RequestService
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
 
 
#Creamos app de flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbpeticiones.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app_context = app.app_context()
app_context.push()

#Inicializamos la base de datos
db.init_app(app)
db.create_all()

#Ponemos rutas de microservicios
microservicios = {'login': 'http://localhost:5001',
                  'ventas': 'http://localhost:5002'}

def conteoPeticiones(usuario):
    #Definimos la hora hace dos minutos
    hora_dos_minutos = datetime.now() - timedelta(minutes = 2)

    #Contamos las peticiones del usuario
    contador = RequestService.query.filter(RequestService.usuario == usuario, RequestService.fecha_peticion >= hora_dos_minutos).count()

    return contador

@app.before_request
def bloqueoUsuario():
    #Definimos el umbral de peticiones
    umbral = 10

    #Extraemos el usuario de la peticion
    usuario = request.headers.get('nombre')

    #Validamos la cantidad de request del usuario
    if conteoPeticiones(usuario) >= umbral:
        return jsonify({'mensaje': 'Usuario bloqueado por exceso de peticiones'}), 403
    
    #Creamos los datos para la persistencia
    request_service = RequestService(usuario = usuario)

    db.session.add(request_service)
    db.session.commit()

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