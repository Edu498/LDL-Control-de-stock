import mysql.connector
from models import Venta, DetalleVenta
from utils.database import get_connection
from datetime import datetime

class VentaController:
    @staticmethod
    def registrar_venta(venta):
        conexion = get_connection()
        cursor = conexion.cursor()
        
        try:
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
                
                cursor.execute("SELECT stock_actual FROM productos WHERE id_producto = %s", (detalle.id_producto,))
                stock_actual = cursor.fetchone()[0]
                stock_nuevo = stock_actual - detalle.cantidad
                
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
            print(f" Venta {venta.numero_factura} registrada - Total: ${total:.2f}")
            return venta
            
        except Exception as e:
            conexion.rollback()
            print(f" Error: {e}")
            raise e
        finally:
            cursor.close()
            conexion.close()
    
    @staticmethod
    def get_ventas_hoy():
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT v.*, 
                   COUNT(dv.id_detalle) as cantidad_productos
            FROM ventas v
            LEFT JOIN detalles_venta dv ON v.id_venta = dv.id_venta
            WHERE DATE(v.fecha_venta) = CURDATE()
            GROUP BY v.id_venta
            ORDER BY v.fecha_venta DESC
        """)
        
        ventas = cursor.fetchall()
        cursor.close()
        conexion.close()
        return ventas
    
    @staticmethod
    def get_resumen_dia():
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                COALESCE(COUNT(*), 0) as total_ventas,
                COALESCE(SUM(total), 0) as monto_total,
                COALESCE(AVG(total), 0) as promedio_venta
            FROM ventas
            WHERE DATE(fecha_venta) = CURDATE()
            AND id_estado = 2
        """)
        
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()
        
        if not resultado or resultado['total_ventas'] is None:
            return {'total_ventas': 0, 'monto_total': 0, 'promedio_venta': 0}
        return resultado