from utils.database import get_connection, execute_query, close_connection
from datetime import datetime

class PedidoController:
    """
    Controlador para la gestión y generación de pedidos a proveedores.
    """
    
    @staticmethod
    def generar_pedido_automatico():
        """
        Genera pedidos automáticos agrupados por proveedor para todos los 
        productos que se encuentren por debajo de su umbral de stock mínimo.
        
        Returns:
            list: Una lista con los IDs de los pedidos generados exitosamente.
        """
        conexion = None
        cursor = None
        
        try:
            conexion = get_connection()
            cursor = conexion.cursor()
            conexion.start_transaction()
            
            cursor.execute("""
                SELECT 
                    p.id_proveedor,
                    vsa.proveedor,
                    GROUP_CONCAT(vsa.id_producto) as productos,
                    GROUP_CONCAT(vsa.cantidad_recomendada) as cantidades,
                    GROUP_CONCAT(vsa.nombre) as nombres
                FROM vw_stock_alertas vsa
                JOIN productos p ON vsa.id_producto = p.id_producto
                WHERE vsa.stock_actual < vsa.stock_minimo 
                AND p.id_proveedor IS NOT NULL
                GROUP BY p.id_proveedor, vsa.proveedor
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
            print(f"✅ Se generaron {len(pedidos_generados)} pedidos automáticos")
            return pedidos_generados
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"❌ Error al generar pedido automático: {e}")
            return []
        finally:
            close_connection(conexion, cursor)
    
    @staticmethod
    def generar_pedido_seleccionados(productos_ids, cantidades_pedir=None):
        """
        Genera pedidos automáticos agrupados por proveedor para los productos 
        seleccionados que se encuentren por debajo de su umbral de stock mínimo.
        
        Args:
            productos_ids (list): Lista de IDs de productos a incluir.
            cantidades_pedir (dict, optional): Diccionario que mapea id_producto -> cantidad_a_pedir.
        Returns:
            list: Una lista con los IDs de los pedidos generados exitosamente.
        """
        if not productos_ids:
            return []
            
        conexion = None
        cursor = None
        
        try:
            conexion = get_connection()
            cursor = conexion.cursor()
            conexion.start_transaction()
            
            # Crear placeholders para la consulta
            placeholders = ','.join(['%s'] * len(productos_ids))
            
            query = f"""
                SELECT 
                    p.id_proveedor,
                    vsa.proveedor,
                    GROUP_CONCAT(vsa.id_producto) as productos,
                    GROUP_CONCAT(vsa.cantidad_recomendada) as cantidades,
                    GROUP_CONCAT(vsa.nombre) as nombres
                FROM vw_stock_alertas vsa
                JOIN productos p ON vsa.id_producto = p.id_producto
                WHERE p.id_producto IN ({placeholders})
                AND p.id_proveedor IS NOT NULL
                GROUP BY p.id_proveedor, vsa.proveedor
            """
            
            cursor.execute(query, tuple(productos_ids))
            proveedores = cursor.fetchall()
            
            if not proveedores:
                print("No hay proveedores para los productos seleccionados")
                return []
            
            pedidos_generados = []
            
            for proveedor in proveedores:
                id_prov = proveedor[0]
                nombre_prov = proveedor[1]
                productos_ids_str = str(proveedor[2]).split(',') if proveedor[2] else []
                cantidades = str(proveedor[3]).split(',') if proveedor[3] else []
                
                if not productos_ids_str:
                    continue
                
                # Crear pedido
                numero_pedido = f"AUTO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{id_prov}"
                cursor.execute("""
                    INSERT INTO pedidos (numero_pedido, id_proveedor, fecha_pedido, id_estado, observaciones)
                    VALUES (%s, %s, NOW(), 1, %s)
                """, (numero_pedido, id_prov, f"Pedido automático personalizado - {nombre_prov}"))
                
                id_pedido = cursor.lastrowid
                pedidos_generados.append(id_pedido)
                
                # Procesar productos del pedido
                detalles_insertados = 0
                for i, id_prod in enumerate(productos_ids_str):
                    try:
                        id_prod_int = int(id_prod)
                        cantidad = 5
                        if cantidades_pedir and id_prod_int in cantidades_pedir:
                            cantidad = cantidades_pedir[id_prod_int]
                        else:
                            cantidad = int(cantidades[i]) if i < len(cantidades) else 5
                            
                        if cantidad <= 0:
                            continue
                        
                        # Obtener precio de compra del producto
                        cursor.execute("SELECT precio_compra FROM productos WHERE id_producto = %s", (id_prod_int,))
                        precio = cursor.fetchone()
                        precio_unitario = precio[0] if precio and precio[0] else 0
                        
                        cursor.execute("""
                            INSERT INTO detalles_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (id_pedido, id_prod_int, cantidad, precio_unitario, cantidad * precio_unitario))
                        detalles_insertados += 1
                    except Exception as e:
                        print(f"Error al agregar producto {id_prod}: {e}")
                
                # Si no se insertaron detalles, eliminar la cabecera del pedido
                if detalles_insertados == 0:
                    cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s", (id_pedido,))
                    pedidos_generados.remove(id_pedido)
                    continue
                
                # Actualizar total del pedido
                cursor.execute("""
                    UPDATE pedidos 
                    SET subtotal = (SELECT COALESCE(SUM(subtotal), 0) FROM detalles_pedido WHERE id_pedido = %s),
                        iva = (SELECT COALESCE(SUM(subtotal), 0) FROM detalles_pedido WHERE id_pedido = %s) * 0.21,
                        total = (SELECT COALESCE(SUM(subtotal), 0) FROM detalles_pedido WHERE id_pedido = %s) * 1.21
                    WHERE id_pedido = %s
                """, (id_pedido, id_pedido, id_pedido, id_pedido))
            
            conexion.commit()
            print(f"✅ Se generaron {len(pedidos_generados)} pedidos automáticos para los productos seleccionados")
            return pedidos_generados
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"❌ Error al generar pedido para seleccionados: {e}")
            return []
        finally:
            close_connection(conexion, cursor)
    
    @staticmethod
    def get_pedidos_pendientes():
        """
        Obtiene todos los pedidos que se encuentran en estado pendiente o enviado.
        
        Returns:
            list: Lista de diccionarios con la información de los pedidos y sus proveedores.
        """
        query = """
            SELECT p.*, pr.nombre as proveedor_nombre,
                   (SELECT COUNT(*) FROM detalles_pedido WHERE id_pedido = p.id_pedido) as cantidad_productos
            FROM pedidos p
            JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
            WHERE p.id_estado IN (1, 2)
            ORDER BY p.fecha_pedido DESC
        """
        return execute_query(query, fetch_all=True)
    
    @staticmethod
    def get_detalles_pedido(id_pedido):
        """
        Obtiene la lista de productos y subtotales vinculados a un pedido específico.
        
        Args:
            id_pedido (int): Identificador único del pedido.
            
        Returns:
            list: Lista de diccionarios con los detalles de los productos del pedido.
        """
        query = """
            SELECT dp.*, p.nombre as producto_nombre, p.codigo
            FROM detalles_pedido dp
            JOIN productos p ON dp.id_producto = p.id_producto
            WHERE dp.id_pedido = %s
        """
        return execute_query(query, params=(id_pedido,), fetch_all=True)
    
    @staticmethod
    def recibir_pedido(id_pedido, usuario, cantidades_recibidas=None):
        """
        Registra la recepción de un pedido, actualizando el estado del pedido,
        la fecha de entrega, el stock de los productos y registrando los
        movimientos de stock correspondientes.
        
        Args:
            id_pedido (int): ID del pedido a recibir.
            usuario (str): Nombre del usuario que realiza la acción.
            cantidades_recibidas (dict, optional): Diccionario que mapea id_producto -> cantidad_recibida.
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario.
        """
        conexion = None
        cursor = None
        
        try:
            conexion = get_connection()
            cursor = conexion.cursor(dictionary=True)
            conexion.start_transaction()
            
            # 1. Obtener información del pedido
            cursor.execute("""
                SELECT numero_pedido, id_estado 
                FROM pedidos 
                WHERE id_pedido = %s
            """, (id_pedido,))
            pedido = cursor.fetchone()
            
            if not pedido:
                print(f"Error: Pedido con ID {id_pedido} no encontrado")
                return False
                
            if pedido['id_estado'] == 3: # Ya recibido
                print(f"Error: El pedido N° {pedido['numero_pedido']} ya fue recibido anteriormente")
                return False
                
            # 2. Obtener los detalles del pedido
            cursor.execute("""
                SELECT id_producto, cantidad 
                FROM detalles_pedido 
                WHERE id_pedido = %s
            """, (id_pedido,))
            detalles = cursor.fetchall()
            
            if not detalles:
                print(f"Error: El pedido N° {pedido['numero_pedido']} no tiene productos asociados")
                return False
                
            # 3. Actualizar stock de los productos y registrar movimientos
            for d in detalles:
                id_prod = d['id_producto']
                
                # Obtener la cantidad recibida específica o por defecto la cantidad pedida
                cantidad_recibida = d['cantidad']
                if cantidades_recibidas and id_prod in cantidades_recibidas:
                    cantidad_recibida = cantidades_recibidas[id_prod]
                
                # Actualizar cantidad_recibida en detalles_pedido
                cursor.execute("""
                    UPDATE detalles_pedido 
                    SET cantidad_recibida = %s 
                    WHERE id_pedido = %s AND id_producto = %s
                """, (cantidad_recibida, id_pedido, id_prod))
                
                if cantidad_recibida <= 0:
                    continue
                
                # Obtener stock actual antes de la actualización
                cursor.execute("""
                    SELECT stock_actual, nombre 
                    FROM productos 
                    WHERE id_producto = %s
                """, (id_prod,))
                prod = cursor.fetchone()
                
                if not prod:
                    print(f"Advertencia: Producto con ID {id_prod} no encontrado. Se omitirá.")
                    continue
                    
                stock_antes = prod['stock_actual']
                stock_despues = stock_antes + cantidad_recibida
                
                # Actualizar stock del producto
                cursor.execute("""
                    UPDATE productos 
                    SET stock_actual = %s 
                    WHERE id_producto = %s
                """, (stock_despues, id_prod))
                
                # Registrar movimiento de stock (Compra: id_tipo_movimiento = 2)
                cursor.execute("""
                    INSERT INTO movimientos_stock 
                        (id_producto, id_tipo_movimiento, cantidad, stock_antes, stock_despues, 
                         referencia_tipo, referencia_id, observacion, usuario, fecha)
                    VALUES (%s, 2, %s, %s, %s, 'pedido', %s, %s, %s, NOW())
                """, (id_prod, cantidad_recibida, stock_antes, stock_despues, 
                      id_pedido, f"Recepción de pedido N° {pedido['numero_pedido']}", usuario))
                      
            # 4. Actualizar estado y fecha de entrega real del pedido
            cursor.execute("""
                UPDATE pedidos 
                SET id_estado = 3, -- Recibido
                    fecha_entrega_real = NOW() 
                WHERE id_pedido = %s
            """, (id_pedido,))
            
            conexion.commit()
            print(f"✅ Pedido N° {pedido['numero_pedido']} recibido y stock actualizado exitosamente")
            return True
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"❌ Error al recibir pedido: {e}")
            raise e
        finally:
            close_connection(conexion, cursor)
            
    @staticmethod
    def get_historial_pedidos():
        """
        Obtiene el historial de pedidos finalizados (recibidos o cancelados).
        
        Returns:
            list: Lista de diccionarios con la información de los pedidos finalizados.
        """
        query = """
            SELECT p.*, pr.nombre as proveedor_nombre,
                   (SELECT COUNT(*) FROM detalles_pedido WHERE id_pedido = p.id_pedido) as cantidad_productos,
                   ep.nombre as estado_nombre
            FROM pedidos p
            JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
            JOIN estados_pedido ep ON p.id_estado = ep.id_estado
            WHERE p.id_estado IN (3, 4)
            ORDER BY p.fecha_entrega_real DESC, p.fecha_pedido DESC
        """
        return execute_query(query, fetch_all=True)