from flask import Flask, request, jsonify
import requests

#Creamos app
app = Flask(__name__)

#Ponemos rutas de microservicios
microservicios = {'ventas': 'http://localhost:5001'}

#Funcion para mandar solicitud a microservicio
def envioSolicitud(microservicio, ruta):

    #Traemos el microservicio por parametro
    url = microservicios[microservicio] + ruta

    #Tipo de peticion
    peticion = request.method

    #Enviamos solicitud
    response = requests.request(peticion, url, json = request.json, headers = request.headers)

    return jsonify(response.json()), response.status_code

#Rutas de los microservicios
@app.route('/ventas', methods = ['GET', 'POST'])
def ventas():
    return envioSolicitud('ventas', '/ventas')

