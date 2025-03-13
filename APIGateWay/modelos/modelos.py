from rol import Rol
from flask_sqlalchemy import SQLAlchemy

#Creamos la base de datos
db = SQLAlchemy()

class RequestService(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    usuario = db.Column(db.String(128))
    fecha_peticion = db.Column(db.DateTime, default = db.func.now())

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(128))
    contrasenia = db.Column(db.String(128))
    rol = db.Column(db.Enum(Rol))
    estado = db.Column(db.Boolean, default = True)