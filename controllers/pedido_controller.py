# controllers/pedido_controller.py
from utils.database import get_connection
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
                    proveedor,
                    GROUP_CONCAT(id_producto) as productos,
                    GROUP_CONCAT(cantidad_recomendada) as cantidades,
                    GROUP_CONCAT(nombre) as nombres
                FROM vw_stock_alertas 
                WHERE estado_stock IN ('STOCK BAJO', 'SIN STOCK') 
                AND proveedor != 'Sin proveedor'
                AND id_proveedor IS NOT NULL
                GROUP BY id_proveedor, proveedor
            """)
            
            proveedores = cursor.fetchall()
            
            if not proveedores:
                print("No hay productos con stock bajo que tengan proveedor asignado")
                return []
            
            pedidos_generados = []
            
            for proveedor in proveedores:
                id_prov = proveedor[0]
                nombre_prov = proveedor[1]
                productos_ids = str(proveedor[2]).split(',') if proveedor[2] else []
                cantidades = str(proveedor[3]).split(',') if proveedor[3] else []
                
                if not productos_ids:
                    continue
                
                # Crear pedido
                numero_pedido = f"AUTO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{id_prov}"
                cursor.execute("""
                    INSERT INTO pedidos (numero_pedido, id_proveedor, fecha_pedido, id_estado, observaciones)
                    VALUES (%s, %s, NOW(), 1, %s)
                """, (numero_pedido, id_prov, f"Pedido automático por stock bajo - {nombre_prov}"))
                
                id_pedido = cursor.lastrowid
                pedidos_generados.append(id_pedido)
                
                # Procesar productos del pedido
                for i, id_prod in enumerate(productos_ids):
                    try:
                        cantidad = int(cantidades[i]) if i < len(cantidades) else 5
                        if cantidad <= 0:
                            cantidad = 5
                        
                        # Obtener precio de compra del producto
                        cursor.execute("SELECT precio_compra FROM productos WHERE id_producto = %s", (id_prod,))
                        precio = cursor.fetchone()
                        precio_unitario = precio[0] if precio and precio[0] else 0
                        
                        cursor.execute("""
                            INSERT INTO detalles_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (id_pedido, id_prod, cantidad, precio_unitario, cantidad * precio_unitario))
                    except Exception as e:
                        print(f"Error al agregar producto {id_prod}: {e}")
                
                # Actualizar total del pedido
                cursor.execute("""
                    UPDATE pedidos 
                    SET subtotal = (SELECT COALESCE(SUM(subtotal), 0) FROM detalles_pedido WHERE id_pedido = %s),
                        iva = (SELECT COALESCE(SUM(subtotal), 0) FROM detalles_pedido WHERE id_pedido = %s) * 0.21,
                        total = (SELECT COALESCE(SUM(subtotal), 0) FROM detalles_pedido WHERE id_pedido = %s) * 1.21
                    WHERE id_pedido = %s
                """, (id_pedido, id_pedido, id_pedido, id_pedido))
            
            conexion.commit()
            print(f" Se generaron {len(pedidos_generados)} pedidos automáticos")
            return pedidos_generados
            
        except Exception as e:
            conexion.rollback()
            print(f" Error al generar pedido automático: {e}")
            return []
        finally:
            cursor.close()
            conexion.close()
    
    @staticmethod
    def get_pedidos_pendientes():
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT p.*, pr.nombre as proveedor_nombre,
                   (SELECT COUNT(*) FROM detalles_pedido WHERE id_pedido = p.id_pedido) as cantidad_productos
            FROM pedidos p
            JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
            WHERE p.id_estado IN (1, 2)
            ORDER BY p.fecha_pedido DESC
        """)
        
        pedidos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return pedidos
    
    @staticmethod
    def get_detalles_pedido(id_pedido):
        """Obtiene los detalles de un pedido específico"""
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT dp.*, p.nombre as producto_nombre, p.codigo
            FROM detalles_pedido dp
            JOIN productos p ON dp.id_producto = p.id_producto
            WHERE dp.id_pedido = %s
        """, (id_pedido,))
        
        detalles = cursor.fetchall()
        cursor.close()
        conexion.close()
        return detalles