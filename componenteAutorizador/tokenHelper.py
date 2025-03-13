from flask_restful import Resource
from flask_jwt_extended import create_access_token

class TokenHelper(Resource):
    @staticmethod
    def createToken(usuario):
        #Extraemos el rol del usuario
        rol = int(usuario.rol.value)

        #Creamos el token con el nombre del usuario y el rol
        access_token = create_access_token(identity = usuario.nombre, additional_claims = {'rol': rol})

        return access_token