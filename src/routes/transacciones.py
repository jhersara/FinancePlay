from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.transaccion import Transaccion
from src.models.categoria import Categoria
from datetime import datetime, date
from sqlalchemy import func, extract

transacciones_bp = Blueprint('transacciones', __name__)

@transacciones_bp.route('/transacciones', methods=['GET'])
def get_transacciones():
    """Obtener todas las transacciones con filtros opcionales"""
    try:
        # Por simplicidad, usamos usuario_id = 1 (primer usuario)
        usuario_id = 1
        
        # Filtros opcionales
        tipo = request.args.get('tipo')  # 'ingreso' o 'gasto'
        categoria_id = request.args.get('categoria_id')
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        query = Transaccion.query.filter_by(usuario_id=usuario_id)
        
        if tipo:
            query = query.filter_by(tipo=tipo)
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        if fecha_inicio:
            query = query.filter(Transaccion.fecha >= datetime.strptime(fecha_inicio, '%Y-%m-%d').date())
        if fecha_fin:
            query = query.filter(Transaccion.fecha <= datetime.strptime(fecha_fin, '%Y-%m-%d').date())
        
        transacciones = query.order_by(Transaccion.fecha.desc()).all()
        
        return jsonify([t.to_dict() for t in transacciones])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transacciones_bp.route('/transacciones', methods=['POST'])
def create_transaccion():
    """Crear una nueva transacción"""
    try:
        data = request.get_json()
        
        # Validaciones básicas
        if not data.get('descripcion'):
            return jsonify({'error': 'La descripción es requerida'}), 400
        if not data.get('monto'):
            return jsonify({'error': 'El monto es requerido'}), 400
        if not data.get('categoria_id'):
            return jsonify({'error': 'La categoría es requerida'}), 400
        if not data.get('tipo') or data.get('tipo') not in ['ingreso', 'gasto']:
            return jsonify({'error': 'El tipo debe ser "ingreso" o "gasto"'}), 400
        
        # Verificar que la categoría existe
        categoria = Categoria.query.get(data.get('categoria_id'))
        if not categoria:
            return jsonify({'error': 'La categoría no existe'}), 400
        
        # Crear la transacción
        transaccion = Transaccion(
            descripcion=data['descripcion'],
            monto=float(data['monto']),
            fecha=datetime.strptime(data.get('fecha', date.today().isoformat()), '%Y-%m-%d').date(),
            tipo=data['tipo'],
            usuario_id=1,  # Por simplicidad, usamos usuario_id = 1
            categoria_id=data['categoria_id']
        )
        
        db.session.add(transaccion)
        db.session.commit()
        
        return jsonify(transaccion.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transacciones_bp.route('/transacciones/<int:transaccion_id>', methods=['PUT'])
def update_transaccion(transaccion_id):
    """Actualizar una transacción existente"""
    try:
        transaccion = Transaccion.query.get_or_404(transaccion_id)
        data = request.get_json()
        
        # Actualizar campos si están presentes
        if 'descripcion' in data:
            transaccion.descripcion = data['descripcion']
        if 'monto' in data:
            transaccion.monto = float(data['monto'])
        if 'fecha' in data:
            transaccion.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        if 'tipo' in data and data['tipo'] in ['ingreso', 'gasto']:
            transaccion.tipo = data['tipo']
        if 'categoria_id' in data:
            categoria = Categoria.query.get(data['categoria_id'])
            if not categoria:
                return jsonify({'error': 'La categoría no existe'}), 400
            transaccion.categoria_id = data['categoria_id']
        
        db.session.commit()
        return jsonify(transaccion.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transacciones_bp.route('/transacciones/<int:transaccion_id>', methods=['DELETE'])
def delete_transaccion(transaccion_id):
    """Eliminar una transacción"""
    try:
        transaccion = Transaccion.query.get_or_404(transaccion_id)
        db.session.delete(transaccion)
        db.session.commit()
        return jsonify({'message': 'Transacción eliminada correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transacciones_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Obtener datos del dashboard principal"""
    try:
        usuario_id = 1  # Por simplicidad
        
        # Obtener transacciones del mes actual
        mes_actual = date.today().month
        año_actual = date.today().year
        
        transacciones_mes = Transaccion.query.filter(
            Transaccion.usuario_id == usuario_id,
            extract('month', Transaccion.fecha) == mes_actual,
            extract('year', Transaccion.fecha) == año_actual
        ).all()
        
        # Calcular totales
        ingresos_mes = sum(t.monto for t in transacciones_mes if t.tipo == 'ingreso')
        gastos_mes = sum(t.monto for t in transacciones_mes if t.tipo == 'gasto')
        balance_mes = ingresos_mes - gastos_mes
        
        # Balance total (todas las transacciones)
        todas_transacciones = Transaccion.query.filter_by(usuario_id=usuario_id).all()
        ingresos_total = sum(t.monto for t in todas_transacciones if t.tipo == 'ingreso')
        gastos_total = sum(t.monto for t in todas_transacciones if t.tipo == 'gasto')
        balance_total = ingresos_total - gastos_total
        
        # Últimas 5 transacciones
        ultimas_transacciones = Transaccion.query.filter_by(usuario_id=usuario_id)\
            .order_by(Transaccion.fecha.desc()).limit(5).all()
        
        return jsonify({
            'balance_total': float(balance_total),
            'ingresos_mes': float(ingresos_mes),
            'gastos_mes': float(gastos_mes),
            'balance_mes': float(balance_mes),
            'ultimas_transacciones': [t.to_dict() for t in ultimas_transacciones]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

