from rol import Rol
from tokenHelper import TokenHelper
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from modelos import db, Usuario, RequestService

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
