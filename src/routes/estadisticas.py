from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.transaccion import Transaccion
from src.models.categoria import Categoria
from sqlalchemy import func, extract
from datetime import datetime, date
from collections import defaultdict

estadisticas_bp = Blueprint('estadisticas', __name__)

@estadisticas_bp.route('/estadisticas/resumen-mensual', methods=['GET'])
def get_resumen_mensual():
    """Obtener resumen de ingresos y gastos por mes"""
    try:
        usuario_id = 1
        año = request.args.get('año', date.today().year, type=int)
        
        # Consulta para obtener totales por mes
        resultados = db.session.query(
            extract('month', Transaccion.fecha).label('mes'),
            Transaccion.tipo,
            func.sum(Transaccion.monto).label('total')
        ).filter(
            Transaccion.usuario_id == usuario_id,
            extract('year', Transaccion.fecha) == año
        ).group_by(
            extract('month', Transaccion.fecha),
            Transaccion.tipo
        ).all()
        
        # Organizar datos por mes
        datos_mensuales = defaultdict(lambda: {'ingresos': 0, 'gastos': 0})
        
        for resultado in resultados:
            mes, tipo, total = resultado
            datos_mensuales[int(mes)][tipo + 's'] = float(total)
        
        # Convertir a lista ordenada por mes
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        datos_grafica = []
        for i in range(1, 13):
            datos_grafica.append({
                'mes': meses[i-1],
                'numero_mes': i,
                'ingresos': datos_mensuales[i]['ingresos'],
                'gastos': datos_mensuales[i]['gastos'],
                'balance': datos_mensuales[i]['ingresos'] - datos_mensuales[i]['gastos']
            })
        
        return jsonify(datos_grafica)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@estadisticas_bp.route('/estadisticas/por-categoria', methods=['GET'])
def get_estadisticas_categoria():
    """Obtener estadísticas por categoría"""
    try:
        usuario_id = 1
        tipo = request.args.get('tipo', 'gasto')  # 'ingreso' o 'gasto'
        mes = request.args.get('mes', type=int)
        año = request.args.get('año', date.today().year, type=int)
        
        query = db.session.query(
            Categoria.nombre,
            Categoria.color,
            func.sum(Transaccion.monto).label('total'),
            func.count(Transaccion.id).label('cantidad')
        ).join(
            Transaccion, Categoria.id == Transaccion.categoria_id
        ).filter(
            Transaccion.usuario_id == usuario_id,
            Transaccion.tipo == tipo,
            extract('year', Transaccion.fecha) == año
        )
        
        if mes:
            query = query.filter(extract('month', Transaccion.fecha) == mes)
        
        resultados = query.group_by(Categoria.id, Categoria.nombre, Categoria.color).all()
        
        datos_categoria = []
        total_general = sum(float(r.total) for r in resultados)
        
        for resultado in resultados:
            porcentaje = (float(resultado.total) / total_general * 100) if total_general > 0 else 0
            datos_categoria.append({
                'categoria': resultado.nombre,
                'color': resultado.color,
                'total': float(resultado.total),
                'cantidad': resultado.cantidad,
                'porcentaje': round(porcentaje, 2)
            })
        
        # Ordenar por total descendente
        datos_categoria.sort(key=lambda x: x['total'], reverse=True)
        
        return jsonify(datos_categoria)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@estadisticas_bp.route('/estadisticas/tendencias', methods=['GET'])
def get_tendencias():
    """Obtener tendencias de los últimos 6 meses"""
    try:
        usuario_id = 1
        
        # Obtener datos de los últimos 6 meses
        resultados = db.session.query(
            extract('year', Transaccion.fecha).label('año'),
            extract('month', Transaccion.fecha).label('mes'),
            Transaccion.tipo,
            func.sum(Transaccion.monto).label('total')
        ).filter(
            Transaccion.usuario_id == usuario_id
        ).group_by(
            extract('year', Transaccion.fecha),
            extract('month', Transaccion.fecha),
            Transaccion.tipo
        ).order_by(
            extract('year', Transaccion.fecha).desc(),
            extract('month', Transaccion.fecha).desc()
        ).limit(12).all()  # Últimos 6 meses x 2 tipos
        
        # Organizar datos
        tendencias = defaultdict(lambda: {'ingresos': 0, 'gastos': 0})
        
        for resultado in resultados:
            año, mes, tipo, total = resultado
            clave = f"{int(año)}-{int(mes):02d}"
            tendencias[clave][tipo + 's'] = float(total)
        
        # Convertir a lista ordenada
        datos_tendencias = []
        for clave in sorted(tendencias.keys(), reverse=True)[:6]:
            año, mes = clave.split('-')
            meses_nombres = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                           'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
            
            datos_tendencias.append({
                'periodo': f"{meses_nombres[int(mes)]} {año}",
                'año': int(año),
                'mes': int(mes),
                'ingresos': tendencias[clave]['ingresos'],
                'gastos': tendencias[clave]['gastos'],
                'balance': tendencias[clave]['ingresos'] - tendencias[clave]['gastos']
            })
        
        return jsonify(list(reversed(datos_tendencias)))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@estadisticas_bp.route('/estadisticas/metricas', methods=['GET'])
def get_metricas():
    """Obtener métricas clave del usuario"""
    try:
        usuario_id = 1
        
        # Todas las transacciones
        transacciones = Transaccion.query.filter_by(usuario_id=usuario_id).all()
        
        if not transacciones:
            return jsonify({
                'total_transacciones': 0,
                'promedio_ingreso': 0,
                'promedio_gasto': 0,
                'categoria_mas_gastada': None,
                'mes_mayor_ahorro': None
            })
        
        # Métricas básicas
        ingresos = [t for t in transacciones if t.tipo == 'ingreso']
        gastos = [t for t in transacciones if t.tipo == 'gasto']
        
        promedio_ingreso = sum(float(t.monto) for t in ingresos) / len(ingresos) if ingresos else 0
        promedio_gasto = sum(float(t.monto) for t in gastos) / len(gastos) if gastos else 0
        
        # Categoría más gastada
        categoria_gastos = defaultdict(float)
        for gasto in gastos:
            categoria_gastos[gasto.categoria.nombre] += float(gasto.monto)
        
        categoria_mas_gastada = max(categoria_gastos.items(), key=lambda x: x[1]) if categoria_gastos else None
        
        # Mes con mayor ahorro
        ahorros_mensuales = defaultdict(lambda: {'ingresos': 0, 'gastos': 0})
        for t in transacciones:
            clave = f"{t.fecha.year}-{t.fecha.month:02d}"
            if t.tipo == 'ingreso':
                ahorros_mensuales[clave]['ingresos'] += float(t.monto)
            else:
                ahorros_mensuales[clave]['gastos'] += float(t.monto)
        
        mejor_mes = None
        mayor_ahorro = float('-inf')
        for mes, datos in ahorros_mensuales.items():
            ahorro = datos['ingresos'] - datos['gastos']
            if ahorro > mayor_ahorro:
                mayor_ahorro = ahorro
                mejor_mes = mes
        
        return jsonify({
            'total_transacciones': len(transacciones),
            'promedio_ingreso': round(promedio_ingreso, 2),
            'promedio_gasto': round(promedio_gasto, 2),
            'categoria_mas_gastada': {
                'nombre': categoria_mas_gastada[0],
                'total': round(categoria_mas_gastada[1], 2)
            } if categoria_mas_gastada else None,
            'mes_mayor_ahorro': {
                'periodo': mejor_mes,
                'ahorro': round(mayor_ahorro, 2)
            } if mejor_mes else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

