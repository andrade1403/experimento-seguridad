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

#Bloqueamos el acceso a las rutas sin token
API_GATEWAY_KEY = "llavesecreta"

@app.before_request
def validar_api_gateway():
    api_key = request.headers.get("X-API-KEY")
    gateway_header = request.headers.get("X-GATEWAY")

    #Solo acepta peticiones que vengan desde el API Gateway con la llave correcta
    if api_key != API_GATEWAY_KEY or gateway_header != "API_GATEWAY":
        return jsonify({"error": "Acceso no autorizado"}), 403