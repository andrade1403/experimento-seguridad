from rol import Rol
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from tokenHelper import TokenHelper
from APIGateWay.modelos import Usuario

#Creamos la aplicacion de flask para el autorizador
app = Flask(__name__)

#Configuramos la aplicacion para que utilice JWT
app.config["JWT_SECRET_KEY"] = "supersecretkey"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

#Inicializamos el JWTManager
jwt = JWTManager(app)

#Bloqueamos el acceso a las rutas sin token
API_GATEWAY_KEY = "llavesecreta"

@app.before_request
def validar_api_gateway():
    api_key = request.headers.get("X-API-KEY")
    gateway_header = request.headers.get("X-GATEWAY")

    #Solo acepta peticiones que vengan desde el API Gateway con la llave correcta
    if api_key != API_GATEWAY_KEY or gateway_header != "API_GATEWAY":
        return jsonify({"error": "Acceso no autorizado"}), 403

#Ruta para el login
@app.route('/login', methods = ['POST'])
def autorizacion():
    #Extraemos el nombre de usuario y la contraseña del request
    usuarioName = request.json.get('nombre')
    contrasenia = request.json.get('contrasenia')

    #Buscamos el usuario en la lista de usuarios
    usuario = Usuario.query.filter(Usuario.nombre == usuarioName).first()

    if usuario.nombre == usuarioName and usuario.contrasenia == contrasenia:
        token = TokenHelper.createToken(usuario)
        return jsonify({'token': token}), 200
    
    return jsonify({'mensaje': 'Usuario o contraseña incorrectos'}), 401
