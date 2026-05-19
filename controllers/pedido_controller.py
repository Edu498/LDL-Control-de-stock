from utils.database import get_connection
from models import Pedido, DetallePedido
from datetime import datetime

class PedidoController:
    @staticmethod
    def generar_pedido_automatico():
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