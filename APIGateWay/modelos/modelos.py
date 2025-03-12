from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests

#Creamos la base de datos
db = SQLAlchemy()

class RequestService(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    usuario = db.Column(db.String(128))
    fecha_peticion = db.Column(db.DateTime, default = db.func.now())
