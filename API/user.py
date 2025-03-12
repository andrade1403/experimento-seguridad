import uuid

class User:
    def __init__(self, nombre, contrasenia, rol):
        self.id = uuid.uuid4()
        self.nombre = nombre
        self.contrasenia = contrasenia
        self.rol = rol