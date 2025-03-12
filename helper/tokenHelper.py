from flask import jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt
from roles.rol import Rol

class TokenHelper(Resource):
    @staticmethod
    def createToken(usuario):
        rol = usuario.rol.value
        access_token = create_access_token(identity = usuario.nombre, additional_claims = {'rol': int(rol)})
        return access_token