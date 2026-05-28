from utils.database import execute_query
from datetime import datetime, timedelta

class ReporteController:
    """
    Controlador encargado de la generación de reportes y estadísticas,
    incluyendo movimientos de inventario, historial de ventas y métricas de productos.
    """
    
    @staticmethod
    def get_movimientos_stock(id_producto=None, dias=90):
        """
        Obtiene el historial de movimientos de stock, pudiendo filtrar por un 
        producto específico y limitando la búsqueda a los últimos 'n' días.

        Args:
            id_producto (int, optional): ID del producto a filtrar. Si es None, trae todos.
            dias (int, optional): Cantidad de días hacia atrás a consultar. Por defecto 90.

        Returns:
            list: Lista de diccionarios con el detalle de cada movimiento.
        """
        fecha_limite = datetime.now() - timedelta(days=dias)
        
        if id_producto:
            query = """
                SELECT 
                    m.id_movimiento,
                    m.id_producto,
                    m.id_tipo_movimiento,
                    m.cantidad,
                    m.stock_antes,
                    m.stock_despues,
                    m.referencia_tipo,
                    m.referencia_id,
                    m.observacion,
                    m.fecha,
                    m.usuario,
                    p.nombre as producto_nombre,
                    p.codigo as producto_codigo,
                    tm.nombre as tipo_movimiento_nombre
                FROM movimientos_stock m
                JOIN productos p ON m.id_producto = p.id_producto
                JOIN tipos_movimiento tm ON m.id_tipo_movimiento = tm.id_tipo_movimiento
                WHERE m.id_producto = %s AND m.fecha >= %s
                ORDER BY m.fecha DESC
                LIMIT 500
            """
            resultados = execute_query(query, params=(id_producto, fecha_limite), fetch_all=True)
        else:
            query = """
                SELECT 
                    m.id_movimiento,
                    m.id_producto,
                    m.id_tipo_movimiento,
                    m.cantidad,
                    m.stock_antes,
                    m.stock_despues,
                    m.referencia_tipo,
                    m.referencia_id,
                    m.observacion,
                    m.fecha,
                    m.usuario,
                    p.nombre as producto_nombre,
                    p.codigo as producto_codigo,
                    tm.nombre as tipo_movimiento_nombre
                FROM movimientos_stock m
                JOIN productos p ON m.id_producto = p.id_producto
                JOIN tipos_movimiento tm ON m.id_tipo_movimiento = tm.id_tipo_movimiento
                WHERE m.fecha >= %s
                ORDER BY m.fecha DESC
                LIMIT 500
            """
            resultados = execute_query(query, params=(fecha_limite,), fetch_all=True)
        
        resultados = resultados if resultados else []
        print(f"DEBUG: Se encontraron {len(resultados)} movimientos")
        return resultados
    
    @staticmethod
    def get_ventas_por_periodo(fecha_inicio, fecha_fin):
        """
        Obtiene un resumen diario de ventas (cantidad y total facturado) 
        dentro de un rango de fechas especificado.

        Args:
            fecha_inicio (str o datetime): Fecha inicial del período.
            fecha_fin (str o datetime): Fecha final del período.

        Returns:
            list: Lista de diccionarios agrupados por día con sus respectivos totales.
        """
        query = """
            SELECT 
                DATE(fecha_venta) as fecha,
                COUNT(*) as cantidad,
                COALESCE(SUM(total), 0) as total
            FROM ventas
            WHERE DATE(fecha_venta) BETWEEN %s AND %s
            AND id_estado = 2
            GROUP BY DATE(fecha_venta)
            ORDER BY fecha
        """
        resultados = execute_query(query, params=(fecha_inicio, fecha_fin), fetch_all=True)
        return resultados if resultados else []
    
    @staticmethod
    def get_productos_mas_vendidos(limite=10):
        """
        Calcula el ranking de los productos con mayor cantidad de unidades vendidas.

        Args:
            limite (int, optional): Cantidad máxima de productos a retornar. Por defecto 10.

        Returns:
            list: Lista de diccionarios con el ID, nombre, total vendido y facturación.
        """
        query = """
            SELECT 
                p.id_producto,
                p.codigo,
                p.nombre,
                COALESCE(SUM(dv.cantidad), 0) AS total_vendido,
                COUNT(DISTINCT dv.id_venta) AS numero_ventas,
                COALESCE(SUM(dv.subtotal), 0) AS ingreso_total
            FROM productos p
            LEFT JOIN detalles_venta dv ON p.id_producto = dv.id_producto
            LEFT JOIN ventas v ON dv.id_venta = v.id_venta AND v.id_estado = 2
            WHERE p.activo = TRUE
            GROUP BY p.id_producto, p.codigo, p.nombre
            HAVING total_vendido > 0
            ORDER BY total_vendido DESC
            LIMIT %s
        """
        try:
            resultados = execute_query(query, params=(limite,), fetch_all=True)
            return resultados if resultados else []
        except Exception as e:
            print(f"❌ Error en get_productos_mas_vendidos: {e}")
            return []