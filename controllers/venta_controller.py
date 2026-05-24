# -*- coding: utf-8 -*-
"""
Controlador de Ventas y Facturación del Sistema.
"""

import mysql.connector
from models import Venta, DetalleVenta
from utils.database import get_connection
from datetime import datetime

class VentaController:
    """
    Controlador encargado de gestionar las operaciones de ventas y transacciones de caja.

    Proporciona métodos estáticos para registrar nuevas ventas (afectando stock y bitácora),
    y para consultar las ventas y totales del día corriente.
    """

    @staticmethod
    def registrar_venta(venta):
        """
        Registra una venta de productos en la base de datos dentro de una transacción.

        Este proceso realiza múltiples operaciones en la base de datos:
        1. Inserta la venta en la tabla `ventas` con estado Completada (id_estado = 2).
        2. Inserta cada detalle del producto vendido en `detalles_venta`.
        3. Descuenta del inventario actual en `productos` la cantidad correspondiente.
        4. Registra un movimiento de tipo Venta en `movimientos_stock` por cada producto.

        Args:
            venta (Venta): Objeto de tipo `models.Venta` que contiene el cliente, usuario y detalles de venta.

        Returns:
            Venta: El objeto `Venta` con su `id_venta` asignado tras la inserción exitosa.

        Raises:
            Exception: Si falla cualquier inserción SQL o la actualización de stock (provoca Rollback).
        """
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
        """
        Obtiene las ventas registradas durante el día actual.

        Returns:
            list: Lista de diccionarios que representan los registros de ventas de hoy,
                  incluyendo el conteo de tipos de producto en cada venta, ordenados por fecha/hora descendente.
        """
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
        """
        Calcula un resumen estadístico y financiero de las ventas completadas del día.

        Returns:
            dict: Diccionario con el total de ventas (conteo), monto total recaudado y promedio de venta (ticket promedio).
        """
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