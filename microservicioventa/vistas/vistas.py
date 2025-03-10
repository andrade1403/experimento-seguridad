import random
from flask import request
from datetime import datetime
from flask_restful import Resource
from modelos import db, Venta, VentasSchema, EstadoVenta

venta_schema = VentasSchema()
is_available = True 
class VistaVenta(Resource):
    def get(self, id_venta):
        venta = Venta.query.filter(Venta.id == id_venta).first()
        return venta_schema.dump(venta)

    def put(self, id_venta):
            
        venta = Venta.query.filter(Venta.id == id_venta).first()

        if venta is not None:
            fecha_pedido = datetime.strptime(request.json['fecha_pedido'], '%d/%m/%Y')
            fecha_limite = datetime.strptime(request.json['fecha_limite'], '%d/%m/%Y')
            estado = EstadoVenta(request.json['estado'])

            venta.fecha_pedido = fecha_pedido if fecha_pedido is not None else venta.fecha_pedido
            venta.fecha_limite = fecha_limite if fecha_limite is not None else venta.fecha_limite
            venta.estado = estado if estado is not None else venta.estado
        
        else:
            return {'mensaje': 'Venta no encontrada'}, 404
        
        db.session.commit()

        return venta_schema.dump(venta)
    
    def delete(self, id_venta):
        venta = Venta.query.filter(Venta.id == id_venta).first()

        if venta:
            db.session.delete(venta)
            db.session.commit()
        
        else:
            return {'mensaje': 'Venta no encontrada'}, 404
        
        return '', 204

class VistaVentas(Resource):
    def get(self):
        ventas = Venta.query.all()
        return [venta_schema.dump(venta) for venta in ventas]
    
    def post(self):

        fecha_pedido = datetime.strptime(request.json['fecha_pedido'], '%d/%m/%Y')
        fecha_limite = datetime.strptime(request.json['fecha_limite'], '%d/%m/%Y')
        estado = EstadoVenta(request.json['estado'])

        nueva_venta = Venta(fecha_pedido = fecha_pedido,
                            fecha_limite = fecha_limite,
                            estado = estado)
        
        db.session.add(nueva_venta)
        db.session.commit()

        return venta_schema.dump(nueva_venta)

class HealthCheck(Resource):
    def get(self):
        if is_available:
            return '', 200
        else:
            return 'state: failed', 503

    def post(self):
        global is_available
        if is_available:
            is_available = False
            return 'state: failed', 200
        else:
            is_available = True
            return 'state: up', 200