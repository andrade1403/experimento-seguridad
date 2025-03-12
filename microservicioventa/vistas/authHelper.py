from functools import wraps
from flask_jwt_extended import get_jwt, jwt_required
from flask import jsonify, make_response
from .helper import metricas

def roles_required(required_roles, peticion):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            #Variable para extraer informacion del token
            jwt_data = get_jwt()

            #Nombre del usuario
            user_id = jwt_data.get('sub')

            #Rol del usuario
            user_role = jwt_data.get('rol')
            
            #Si el rol del usuario no esta en los roles requeridos, se bloquea la peticion
            if user_role not in required_roles:
                #Se envian las metricas a la API con el estado 403
                metricas(user_id, peticion, 403, True)

                return make_response(jsonify({"msg": "No tienes permisos para acceder a esta información"}), 403)

            #Se envian las metricas a la API con el estado 200
            metricas(user_id, peticion, 200, False)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
