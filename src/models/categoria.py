from src.models.user import db

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'ingreso' o 'gasto'
    color = db.Column(db.String(7), default='#FF6B35')  # Color en formato hex
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relación con transacciones
    transacciones = db.relationship('Transaccion', backref='categoria', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Categoria {self.nombre} ({self.tipo})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'color': self.color,
            'usuario_id': self.usuario_id
        }

