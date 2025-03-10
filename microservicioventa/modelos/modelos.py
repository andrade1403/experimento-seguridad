import enum
from marshmallow import fields, Schema
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class EstadoVenta(enum.Enum):
    SOLICITADO = 1
    ENVIADO = 2
    ENTREGADO = 3
    CANCELADO = 4

class Venta(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    fecha_pedido = db.Column(db.DateTime)
    fecha_limite = db.Column(db.DateTime)
    estado = db.Column(db.Enum(EstadoVenta))

class EnumDiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        
        return {'llave': value.name, 'valor': value.value}

class VentasSchema(SQLAlchemyAutoSchema):
    estado = EnumDiccionario(attribute=('rol'))
    class Meta:
        model = Venta
        load_instance = True
        
    id = fields.String()