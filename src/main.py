import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.categoria import Categoria
from src.models.transaccion import Transaccion
from src.routes.user import user_bp
from src.routes.transacciones import transacciones_bp
from src.routes.categorias import categorias_bp
from src.routes.estadisticas import estadisticas_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para todas las rutas
CORS(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(transacciones_bp, url_prefix='/api')
app.register_blueprint(categorias_bp, url_prefix='/api')
app.register_blueprint(estadisticas_bp, url_prefix='/api')

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def init_database():
    """Inicializar base de datos con datos de ejemplo"""
    with app.app_context():
        db.create_all()
        
        # Verificar si ya existen datos
        if not db.session.query(db.session.query(Categoria).exists()).scalar():
            # Crear usuario de ejemplo
            from src.models.user import User
            usuario = User(username='demo', email='demo@finanzas.com')
            db.session.add(usuario)
            db.session.flush()  # Para obtener el ID
            
            # Crear categorías de ejemplo
            categorias_ejemplo = [
                # Categorías de gastos
                Categoria(nombre='Alimentación', tipo='gasto', color='#FF6B35', usuario_id=usuario.id),
                Categoria(nombre='Transporte', tipo='gasto', color='#FF8C42', usuario_id=usuario.id),
                Categoria(nombre='Entretenimiento', tipo='gasto', color='#FFD23F', usuario_id=usuario.id),
                Categoria(nombre='Servicios', tipo='gasto', color='#FF4757', usuario_id=usuario.id),
                Categoria(nombre='Salud', tipo='gasto', color='#FF6348', usuario_id=usuario.id),
                # Categorías de ingresos
                Categoria(nombre='Salario', tipo='ingreso', color='#2ECC71', usuario_id=usuario.id),
                Categoria(nombre='Freelance', tipo='ingreso', color='#27AE60', usuario_id=usuario.id),
                Categoria(nombre='Inversiones', tipo='ingreso', color='#16A085', usuario_id=usuario.id),
            ]
            
            for categoria in categorias_ejemplo:
                db.session.add(categoria)
            
            db.session.commit()
            print("Base de datos inicializada con datos de ejemplo")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
