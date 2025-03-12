from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from API.user import User
from roles.rol import Rol
from helper.tokenHelper import TokenHelper

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "supersecretkey"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

jwt = JWTManager(app)

usuarios = [User('usuario1', 'pass1', Rol.DIRECTOR), User('usuario2', 'pass2', Rol.OPERARIO)]

@app.route('/login', methods=['POST'])
def autorizacion():
    usuarioName = request.json.get('nombre')
    contrasenia = request.json.get('contrasenia')

    for usuario in usuarios:
        if usuario.nombre == usuarioName and usuario.contrasenia == contrasenia:
            token = TokenHelper.createToken(usuario)
            return jsonify({'token': token}), 200
    
    return jsonify({'mensaje': 'Usuario o contraseña incorrectos'}), 401
