import requests
from flask import Flask, request, jsonify
 
 
#Creamos app de flask
app = Flask(__name__)

#Ponemos rutas de microservicios
microservicios = {'login': 'http://localhost:5001',
                  'ventas': 'http://localhost:5002'}

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

@app.route('/login', methods = ['POST'])
def login():
    return envioSolicitud('login', '/login')