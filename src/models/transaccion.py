from src.models.user import db
from datetime import datetime

class Transaccion(db.Model):
    __tablename__ = 'transacciones'
    
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'ingreso' o 'gasto'
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Claves foráneas
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    
    def __repr__(self):
        return f'<Transaccion {self.descripcion}: {self.monto}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion,
            'monto': float(self.monto),
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'tipo': self.tipo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'usuario_id': self.usuario_id,
            'categoria_id': self.categoria_id,
            'categoria_nombre': self.categoria.nombre if self.categoria else None,
            'categoria_color': self.categoria.color if self.categoria else None
        }

