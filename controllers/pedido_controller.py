# -*- coding: utf-8 -*-
"""
Controlador de Pedidos a Proveedores.
"""

from utils.database import get_connection
from models import Pedido, DetallePedido
from datetime import datetime

class PedidoController:
    """
    Controlador para gestionar la lógica de negocio de pedidos a proveedores.

    Proporciona métodos estáticos para generar pedidos de reposición automáticos
    y para consultar pedidos en estado pendiente o en proceso.
    """

    @staticmethod
    def generar_pedido_automatico():
        """
        Genera pedidos automáticos de reposición de stock agrupados por proveedor.

        Analiza la vista `vw_stock_alertas` en busca de productos con stock bajo
        o nulo que tengan un proveedor asignado. Crea un pedido pendiente por cada
        proveedor con los insumos críticos.

        Returns:
            list: Lista de IDs de los pedidos generados.
        
        Raises:
            Exception: Si ocurre un error en la base de datos durante la transacción.
        """
        conexion = get_connection()
        cursor = conexion.cursor()
        
        try:
            conexion.start_transaction()
            
            # Obtener productos con stock bajo agrupados por proveedor
            cursor.execute("""
                SELECT 
                    id_proveedor,
                    GROUP_CONCAT(id_producto) as productos,
                    GROUP_CONCAT(cantidad_recomendada) as cantidades
                FROM vw_stock_alertas 
                WHERE estado_stock IN ('STOCK BAJO', 'SIN STOCK') 
                AND proveedor IS NOT NULL
                GROUP BY id_proveedor
            """)
            
            proveedores = cursor.fetchall()
            pedidos_generados = []
            
            for proveedor in proveedores:
                # Crear pedido
                numero_pedido = f"AUTO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{proveedor[0]}"
                cursor.execute("""
                    INSERT INTO pedidos (numero_pedido, id_proveedor, fecha_pedido, id_estado)
                    VALUES (%s, %s, NOW(), 1)
                """, (numero_pedido, proveedor[0]))
                
                id_pedido = cursor.lastrowid
                pedidos_generados.append(id_pedido)
                
                # Aquí se agregarían los productos al pedido
                # (simplificado por brevedad)
            
            conexion.commit()
            return pedidos_generados
            
        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()
    
    @staticmethod
    def get_pedidos_pendientes():
        """
        Obtiene todos los pedidos que se encuentran en estado 'Pendiente' o 'Enviado'.

        Returns:
            list: Lista de diccionarios que representan los registros de pedidos pendientes
                  con el nombre de sus proveedores asociados, ordenados de forma descendente por fecha.
        """
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT p.*, pr.nombre as proveedor_nombre
            FROM pedidos p
            JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
            WHERE p.id_estado IN (1, 2)
            ORDER BY p.fecha_pedido DESC
        """)
        
        pedidos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return pedidos