from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.categoria import Categoria

categorias_bp = Blueprint('categorias', __name__)

@categorias_bp.route('/categorias', methods=['GET'])
def get_categorias():
    """Obtener todas las categorías del usuario"""
    try:
        usuario_id = 1  # Por simplicidad, usamos usuario_id = 1
        tipo = request.args.get('tipo')  # Filtro opcional por tipo
        
        query = Categoria.query.filter_by(usuario_id=usuario_id)
        if tipo and tipo in ['ingreso', 'gasto']:
            query = query.filter_by(tipo=tipo)
        
        categorias = query.order_by(Categoria.nombre).all()
        return jsonify([c.to_dict() for c in categorias])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@categorias_bp.route('/categorias', methods=['POST'])
def create_categoria():
    """Crear una nueva categoría"""
    try:
        data = request.get_json()
        
        # Validaciones
        if not data.get('nombre'):
            return jsonify({'error': 'El nombre es requerido'}), 400
        if not data.get('tipo') or data.get('tipo') not in ['ingreso', 'gasto']:
            return jsonify({'error': 'El tipo debe ser "ingreso" o "gasto"'}), 400
        
        # Verificar que no existe una categoría con el mismo nombre y tipo
        categoria_existente = Categoria.query.filter_by(
            usuario_id=1,
            nombre=data['nombre'],
            tipo=data['tipo']
        ).first()
        
        if categoria_existente:
            return jsonify({'error': 'Ya existe una categoría con ese nombre y tipo'}), 400
        
        categoria = Categoria(
            nombre=data['nombre'],
            tipo=data['tipo'],
            color=data.get('color', '#FF6B35'),
            usuario_id=1  # Por simplicidad
        )
        
        db.session.add(categoria)
        db.session.commit()
        
        return jsonify(categoria.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categorias_bp.route('/categorias/<int:categoria_id>', methods=['PUT'])
def update_categoria(categoria_id):
    """Actualizar una categoría existente"""
    try:
        categoria = Categoria.query.get_or_404(categoria_id)
        data = request.get_json()
        
        if 'nombre' in data:
            categoria.nombre = data['nombre']
        if 'tipo' in data and data['tipo'] in ['ingreso', 'gasto']:
            categoria.tipo = data['tipo']
        if 'color' in data:
            categoria.color = data['color']
        
        db.session.commit()
        return jsonify(categoria.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categorias_bp.route('/categorias/<int:categoria_id>', methods=['DELETE'])
def delete_categoria(categoria_id):
    """Eliminar una categoría"""
    try:
        categoria = Categoria.query.get_or_404(categoria_id)
        
        # Verificar si tiene transacciones asociadas
        if categoria.transacciones:
            return jsonify({'error': 'No se puede eliminar una categoría que tiene transacciones asociadas'}), 400
        
        db.session.delete(categoria)
        db.session.commit()
        return jsonify({'message': 'Categoría eliminada correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

