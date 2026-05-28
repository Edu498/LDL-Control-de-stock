from models import Venta, DetalleVenta
from utils.database import get_connection, execute_query, close_connection
from datetime import datetime

class VentaController:
    """
    Controlador para la gestión de ventas, incluyendo el registro transaccional 
    de comprobantes, descuento de stock en tiempo real y estadísticas diarias.
    """

    @staticmethod
    def registrar_venta(venta):
        """
        Registra una nueva venta de forma transaccional (ACID). Inserta la cabecera,
        los detalles, descuenta el inventario físico y genera el historial de movimientos.
        
        Args:
            venta (Venta): Objeto que contiene los datos de la venta y sus detalles.
            
        Returns:
            Venta: El objeto venta actualizado con su ID generado por la base de datos.
            
        Raises:
            ValueError: Si se intenta vender más stock del disponible.
        """
        conexion = None
        cursor = None
        
        try:
            conexion = get_connection()
            cursor = conexion.cursor()
            conexion.start_transaction()
            
            subtotal = venta.subtotal
            iva = venta.iva
            total = venta.total
            
            cursor.execute("""
                INSERT INTO ventas (numero_factura, cliente_nombre, subtotal, iva, total, usuario, id_estado, fecha_venta)
                VALUES (%s, %s, %s, %s, %s, %s, 2, NOW())
            """, (venta.numero_factura, venta.cliente_nombre, subtotal, iva, total, venta.usuario))
            
            venta.id_venta = cursor.lastrowid
            
            for detalle in venta.detalles:
                cursor.execute("""
                    INSERT INTO detalles_venta (id_venta, id_producto, cantidad, 
                                                precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, (venta.id_venta, detalle.id_producto, detalle.cantidad,
                      detalle.precio_unitario, detalle.subtotal))
                
                cursor.execute("SELECT stock_actual FROM productos WHERE id_producto = %s FOR UPDATE", (detalle.id_producto,))
                resultado_stock = cursor.fetchone()
                
                if not resultado_stock:
                    raise ValueError(f"Producto con ID {detalle.id_producto} no encontrado.")
                    
                stock_actual = resultado_stock[0]
                stock_nuevo = stock_actual - detalle.cantidad
                
                if stock_nuevo < 0:
                    raise ValueError(f"Stock insuficiente para descontar {detalle.cantidad} unidades.")

                cursor.execute("""
                    UPDATE productos 
                    SET stock_actual = %s 
                    WHERE id_producto = %s
                """, (stock_nuevo, detalle.id_producto))
                
                cursor.execute("""
                    INSERT INTO movimientos_stock (id_producto, id_tipo_movimiento, cantidad,
                                                   stock_antes, stock_despues, referencia_tipo,
                                                   referencia_id, usuario, fecha)
                    VALUES (%s, 1, %s, %s, %s, 'venta', %s, %s, NOW())
                """, (detalle.id_producto, -detalle.cantidad, stock_actual, stock_nuevo, venta.id_venta, venta.usuario))
            
            conexion.commit()
            print(f"✅ Venta {venta.numero_factura} registrada - Total: ${total:.2f}")
            return venta
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"❌ Error al registrar venta: {e}")
            raise e
        finally:
            close_connection(conexion, cursor)
    
    @staticmethod
    def get_ventas_hoy():
        """
        Recupera el listado de todas las ventas concretadas en la fecha actual.
        
        Returns:
            list: Lista de diccionarios con la cabecera de la venta y la cantidad de ítems.
        """
        query = """
            SELECT v.*, 
                   COUNT(dv.id_detalle) as cantidad_productos
            FROM ventas v
            LEFT JOIN detalles_venta dv ON v.id_venta = dv.id_venta
            WHERE DATE(v.fecha_venta) = CURDATE()
            GROUP BY v.id_venta
            ORDER BY v.fecha_venta DESC
        """
        return execute_query(query, fetch_all=True)
    
    @staticmethod
    def get_resumen_dia():
        """
        Calcula las estadísticas clave de ingresos de la jornada actual.
        
        Returns:
            dict: Diccionario conteniendo 'total_ventas', 'monto_total' y 'promedio_venta'.
        """
        query = """
            SELECT 
                COALESCE(COUNT(*), 0) as total_ventas,
                COALESCE(SUM(total), 0) as monto_total,
                COALESCE(AVG(total), 0) as promedio_venta
            FROM ventas
            WHERE DATE(fecha_venta) = CURDATE()
            AND id_estado = 2
        """
        resultado = execute_query(query, fetch_one=True)
        
        if not resultado or resultado['total_ventas'] == 0:
            return {'total_ventas': 0, 'monto_total': 0, 'promedio_venta': 0}
        
        return resultado