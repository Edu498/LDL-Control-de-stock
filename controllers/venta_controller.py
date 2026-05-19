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
            
            # Insertar venta
            cursor.execute("""
                INSERT INTO ventas (numero_factura, cliente_nombre, usuario, id_estado)
                VALUES (%s, %s, %s, 2)
            """, (venta.numero_factura, venta.cliente_nombre, venta.usuario))
            
            venta.id_venta = cursor.lastrowid
            
            # Insertar detalles y actualizar stock
            for detalle in venta.detalles:
                cursor.execute("""
                    INSERT INTO detalles_venta (id_venta, id_producto, cantidad, 
                                                precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, (venta.id_venta, detalle.id_producto, detalle.cantidad,
                      detalle.precio_unitario, detalle.subtotal))
                
                # Actualizar stock (cantidad negativa)
                cursor.execute("""
                    UPDATE productos 
                    SET stock_actual = stock_actual - %s 
                    WHERE id_producto = %s
                """, (detalle.cantidad, detalle.id_producto))
                
                # Registrar movimiento
                cursor.execute("""
                    INSERT INTO movimientos_stock (id_producto, id_tipo_movimiento, cantidad,
                                                   stock_antes, stock_despues, referencia_tipo,
                                                   referencia_id, usuario)
                    SELECT %s, 1, -%s, stock_actual + %s, stock_actual, 'venta', %s, %s
                    FROM productos WHERE id_producto = %s
                """, (detalle.id_producto, detalle.cantidad, detalle.cantidad,
                      venta.id_venta, venta.usuario, detalle.id_producto))
            
            conexion.commit()
            return venta
            
        except Exception as e:
            conexion.rollback()
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
                COUNT(*) as total_ventas,
                SUM(total) as monto_total,
                AVG(total) as promedio_venta
            FROM ventas
            WHERE DATE(fecha_venta) = CURDATE()
            AND id_estado = 2
        """)
        
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()
        return resultado