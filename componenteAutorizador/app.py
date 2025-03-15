from rol import Rol
from tokenHelper import TokenHelper
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt
from modelos import db, Usuario, RequestService, UsuarioSchema, RequestServiceSchema

#Creamos app de flask
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "supersecretkey"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbpeticiones.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app_context = app.app_context()
app_context.push()

#Inicializamos la base de datos
db.init_app(app)
db.create_all()

#Creamos los dos usuarios en base de datos
consulta_1 = Usuario.query.filter(Usuario.nombre == 'usuarioExp1').first()
consulta_2 = Usuario.query.filter(Usuario.nombre == 'usuarioExp2').first()

if not (consulta_1 and consulta_2):
    usuario_1 = Usuario(nombre = 'usuarioExp1', contrasenia = 'pass1', rol = Rol.DIRECTOR)
    usuario_2 = Usuario(nombre = 'usuarioExp2', contrasenia = 'pass2', rol = Rol.OPERARIO)
    db.session.add(usuario_1)
    db.session.add(usuario_2)
    db.session.commit()
    
#Inicializamos Schemas
usuario_schema = UsuarioSchema()
request_service_schema = RequestServiceSchema()

#Inicializamos el JWTManager
jwt = JWTManager(app)

#Ruta para el login
@app.route('/login', methods = ['POST'])
def autorizacion():
    #Extraemos el nombre de usuario y la contraseña del request
    usuarioName = request.json.get('nombre')
    contrasenia = request.json.get('contrasenia')

    #Buscamos el usuario en la lista de usuarios
    usuario = Usuario.query.filter(Usuario.nombre == usuarioName).first()

    if usuario:
        if usuario.nombre == usuarioName and usuario.contrasenia == contrasenia:
            token = TokenHelper.createToken(usuario)
            return jsonify({'token': token}), 200
    
    return jsonify({'mensaje': 'Usuario o contraseña incorrectos'}), 401

#Ruta para llevar los usuarios de la base de datos
@app.route('/usuarios', methods = ['GET', 'POST'])
@jwt_required()
def usuarios():
    usuarios = Usuario.query.all()

    usuarios_aux = []
    for usuario in usuarios:
        hash_aux = dict()
        hash_aux['nombre'] = usuario.nombre
        hash_aux['estado'] = usuario.estado
        usuarios_aux.append(hash_aux)

    return jsonify([usuario_schema.dump(usuario) for usuario in usuarios_aux]), 200

#Ruta para traer un usuario por nombre
@app.route('/usuarios/<nombre>', methods=['GET'])
@jwt_required()
def usuario(nombre):
    #Traemos el usuario de la base de datos
    usuario = Usuario.query.filter_by(nombre = nombre).first()

    #Validamos si el usuario existe
    if usuario:
        usuario_aux = {"nombre": usuario.nombre, "estado": usuario.estado}
        return jsonify(usuario_aux)

    return jsonify({'mensaje': 'Usuario no encontrado'}), 404

#Ruta para actualizar el estado del usuario
@app.route('/usuarios/<nombre>', methods = ['PUT'])
def actualizarUsuario(nombre):
    #Traemos el usuario de la base de datos
    usuario = Usuario.query.filter(Usuario.nombre == nombre).first()

    #Validamos si el usuario existe
    if usuario:
        usuario.estado = False
        db.session.commit()
        usuario_aux = {"nombre": usuario.nombre, "estado": usuario.estado}
        return jsonify(usuario_aux), 200
    
    return jsonify({'mensaje': 'Usuario no encontrado'}), 404

#Ruta para crear un request por parte del usuario
@app.route('/peticiones', methods = ['POST'])
@jwt_required()
def peticion():
    #Extraemos el usuario del request
    jwt_data = get_jwt()
    usuarioName = jwt_data['sub']

    #Validamos si el usuario existe
    usuario = Usuario.query.filter(Usuario.nombre == usuarioName).first()

    #Validamos si el usuario existe
    if usuario:
        #Creamos el request
        request_service = RequestService(usuario = usuarioName)
        db.session.add(request_service)
        db.session.commit()

        return request_service_schema.dump(request_service), 200
    
    return jsonify({'mensaje': 'Usuario no encontrado'}), 404

#Ruta para traer las peticiones de un usuario en un tiempo determinado
@app.route('/peticiones/<nombre>', methods = ['GET'])
def peticionesUsuario(nombre):
    #Traemos el usuario de la base de datos
    usuario = Usuario.query.filter(Usuario.nombre == nombre).first()

    #Definimos la hora hace dos minutos
    hora_dos_minutos = datetime.now() - timedelta(minutes = 2)

    #Validamos si el usuario existe
    if usuario:
        #Hacemos el filtro de las peticiones
        peticiones = RequestService.query.filter(RequestService.usuario == nombre, RequestService.fecha_peticion >= hora_dos_minutos).count()
        return jsonify({'contador': peticiones}), 200
    
    return jsonify({'mensaje': 'Usuario no encontrado'}), 404