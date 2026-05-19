from utils.database import get_connection
from datetime import datetime, timedelta

class ReporteController:
    @staticmethod
    def get_ventas_por_periodo(fecha_inicio, fecha_fin):
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
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM vw_productos_mas_vendidos LIMIT %s", (limite,))
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
        return resultados
    
    @staticmethod
    def get_movimientos_stock(id_producto=None, dias=30):
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