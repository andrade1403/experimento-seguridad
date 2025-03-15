from flask import Flask, request, jsonify
from flask_restful import Api
from modelos import db
from vistas import VistaVenta, VistaVentas, HealthCheck
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbexperimento.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "supersecretkey"
jwt = JWTManager(app)
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)
api.add_resource(VistaVenta, '/ventas/<int:id_venta>')
api.add_resource(VistaVentas, '/ventas')
api.add_resource(HealthCheck, '/health')