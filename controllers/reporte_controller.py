# -*- coding: utf-8 -*-
"""
Controlador de Reportes y Estadísticas del Sistema.
"""

from utils.database import get_connection
from datetime import datetime, timedelta

class ReporteController:
    """
    Controlador encargado de agrupar y procesar datos estadísticos.

    Proporciona métodos estáticos para generar reportes financieros y operativos,
    como ventas por período, productos más vendidos e historial de movimientos de inventario.
    """

    @staticmethod
    def get_ventas_por_periodo(fecha_inicio, fecha_fin):
        """
        Obtiene el resumen de ventas agrupadas por día en un rango de fechas.

        Args:
            fecha_inicio (str o date): Fecha de inicio del reporte.
            fecha_fin (str o date): Fecha de fin del reporte.

        Returns:
            list: Lista de diccionarios con la fecha, cantidad de ventas y monto total facturado por día.
        """
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                DATE(fecha_venta) as fecha,
                COUNT(*) as cantidad,
                SUM(total) as total
            FROM ventas
            WHERE DATE(fecha_venta) BETWEEN %s AND %s
            AND id_estado = 2
            GROUP BY DATE(fecha_venta)
            ORDER BY fecha
        """, (fecha_inicio, fecha_fin))
        
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
        return resultados
    
    @staticmethod
    def get_productos_mas_vendidos(limite=10):
        """
        Obtiene los productos con mayor volumen de venta acumulado.

        Args:
            limite (int, opcional): Número máximo de productos a retornar. Por defecto es 10.

        Returns:
            list: Lista de diccionarios que representan los productos más vendidos (código, nombre, cantidad).
        """
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM vw_productos_mas_vendidos LIMIT %s", (limite,))
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
        return resultados
    
    @staticmethod
    def get_movimientos_stock(id_producto=None, dias=30):
        """
        Consulta la bitácora de movimientos de stock (entradas, salidas, mermas).

        Args:
            id_producto (int, opcional): ID del producto específico a filtrar. Si es None, retorna todos.
            dias (int, opcional): Rango de días previos a consultar. Por defecto es 30.

        Returns:
            list: Lista de diccionarios con el historial de movimientos de stock.
        """
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        fecha_limite = datetime.now() - timedelta(days=dias)
        
        if id_producto:
            cursor.execute("""
                SELECT m.*, p.nombre as producto, tm.nombre as tipo_movimiento
                FROM movimientos_stock m
                JOIN productos p ON m.id_producto = p.id_producto
                JOIN tipos_movimiento tm ON m.id_tipo_movimiento = tm.id_tipo_movimiento
                WHERE m.id_producto = %s AND m.fecha >= %s
                ORDER BY m.fecha DESC
            """, (id_producto, fecha_limite))
        else:
            cursor.execute("""
                SELECT m.*, p.nombre as producto, tm.nombre as tipo_movimiento
                FROM movimientos_stock m
                JOIN productos p ON m.id_producto = p.id_producto
                JOIN tipos_movimiento tm ON m.id_tipo_movimiento = tm.id_tipo_movimiento
                WHERE m.fecha >= %s
                ORDER BY m.fecha DESC
                LIMIT 100
            """, (fecha_limite,))
        
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
        return resultados