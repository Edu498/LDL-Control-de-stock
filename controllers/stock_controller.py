import mysql.connector
from models import Producto, Categoria, Proveedor
from utils.database import get_connection

class StockController:
    """Controlador profesional para gestión de stock"""
    
    @staticmethod
    def get_all_productos():
        """Obtiene todos los productos activos con sus relaciones"""
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT p.*, c.nombre as categoria_nombre, pr.nombre as proveedor_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
            LEFT JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
            WHERE p.activo = TRUE
            ORDER BY p.nombre
        """)
        
        productos = []
        for row in cursor.fetchall():
            producto = Producto(
                id_producto=row['id_producto'],
                codigo=row['codigo'],
                nombre=row['nombre'],
                descripcion=row['descripcion'],
                id_categoria=row['id_categoria'],
                id_proveedor=row['id_proveedor'],
                precio_compra=row['precio_compra'],
                precio_venta=row['precio_venta'],
                stock_actual=row['stock_actual'],
                stock_minimo=row['stock_minimo'],
                stock_maximo=row['stock_maximo'],
                ubicacion=row['ubicacion'],
                unidad_medida=row['unidad_medida'],
                activo=row['activo']
            )
            productos.append(producto)
        
        cursor.close()
        conexion.close()
        return productos
    
    @staticmethod
    def get_productos_con_alerta():
        """Obtiene productos con stock crítico (bajo o sin stock)"""
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM vw_stock_alertas
            WHERE estado_stock != 'NORMAL'
            ORDER BY 
                CASE estado_stock
                    WHEN 'SIN STOCK' THEN 1
                    WHEN 'STOCK BAJO' THEN 2
                END,
                stock_actual
        """)
        
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
        return resultados
    
    @staticmethod
    def get_producto_by_id(id_producto):
        """Obtiene un producto específico por su ID"""
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id_producto,))
        row = cursor.fetchone()
        
        cursor.close()
        conexion.close()
        
        if row:
            return Producto(
                id_producto=row['id_producto'],
                codigo=row['codigo'],
                nombre=row['nombre'],
                descripcion=row['descripcion'],
                id_categoria=row['id_categoria'],
                id_proveedor=row['id_proveedor'],
                precio_compra=row['precio_compra'],
                precio_venta=row['precio_venta'],
                stock_actual=row['stock_actual'],
                stock_minimo=row['stock_minimo'],
                stock_maximo=row['stock_maximo'],
                ubicacion=row['ubicacion'],
                unidad_medida=row['unidad_medida'],
                activo=row['activo']
            )
        return None
    
    @staticmethod
    def crear_producto(producto):
        """Crea un nuevo producto en la base de datos"""
        conexion = get_connection()
        cursor = conexion.cursor()
        
        try:
            query = """
                INSERT INTO productos (codigo, nombre, descripcion, id_categoria, id_proveedor,
                                       precio_compra, precio_venta, stock_actual, stock_minimo,
                                       stock_maximo, ubicacion, unidad_medida)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (producto.codigo, producto.nombre, producto.descripcion,
                       producto.id_categoria, producto.id_proveedor, producto.precio_compra,
                       producto.precio_venta, producto.stock_actual, producto.stock_minimo,
                       producto.stock_maximo, producto.ubicacion, producto.unidad_medida)
            
            cursor.execute(query, valores)
            conexion.commit()
            producto.id_producto = cursor.lastrowid
            
            return producto
        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            conexion.close()
    
    @staticmethod
    def actualizar_stock(id_producto, cantidad, tipo_movimiento, usuario, referencia=None):
        """
        Actualiza el stock de un producto y registra el movimiento
        
        Args:
            id_producto: ID del producto
            cantidad: Cantidad a modificar (POSITIVA para ENTRADA, NEGATIVA para SALIDA)
            tipo_movimiento: 1=Venta, 2=Compra, 3=Ajuste+, 4=Ajuste-
            usuario: Usuario que realiza la operación
            referencia: Información adicional de referencia
        """
        # ========== DEBUG ==========
        print(f"\n📊 STOCK CONTROLLER:")
        print(f"   Producto ID: {id_producto}")
        print(f"   Cantidad: {cantidad} ({'ENTRADA' if cantidad > 0 else 'SALIDA'})")
        print(f"   Tipo Movimiento: {tipo_movimiento}")
        print(f"   Usuario: {usuario}")
        # ===========================
        
        conexion = get_connection()
        cursor = conexion.cursor()
        
        try:
            conexion.start_transaction()
            
            # Obtener stock actual con bloqueo para actualización
            cursor.execute("SELECT stock_actual, nombre FROM productos WHERE id_producto = %s FOR UPDATE", (id_producto,))
            resultado = cursor.fetchone()
            
            if not resultado:
                raise ValueError(f"Producto con ID {id_producto} no encontrado")
            
            stock_actual = resultado[0]
            nombre_producto = resultado[1]
            stock_nuevo = stock_actual + cantidad
            
            # Validación de stock negativo
            if stock_nuevo < 0:
                raise ValueError(f"Stock insuficiente. Stock actual: {stock_actual}, intenta quitar: {-cantidad}")
            
            # Actualizar stock del producto
            cursor.execute("""
                UPDATE productos 
                SET stock_actual = %s 
                WHERE id_producto = %s
            """, (stock_nuevo, id_producto))
            
            # Registrar movimiento en historial
            motivo = referencia.get('motivo', 'Ajuste manual') if referencia else 'Ajuste manual'
            referencia_tipo = referencia.get('tipo') if referencia else 'ajuste'
            referencia_id = referencia.get('id') if referencia else None
            
            cursor.execute("""
                INSERT INTO movimientos_stock (id_producto, id_tipo_movimiento, cantidad, 
                                               stock_antes, stock_despues, referencia_tipo, 
                                               referencia_id, usuario, fecha)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (id_producto, tipo_movimiento, cantidad, stock_actual, stock_nuevo,
                  referencia_tipo, referencia_id, usuario))
            
            conexion.commit()
            print(f"✅ Stock actualizado: {nombre_producto} - {stock_actual} → {stock_nuevo} (cantidad: {cantidad})")
            if cantidad > 0:
                print(f"   → TIPO: ENTRADA")
            elif cantidad < 0:
                print(f"   → TIPO: SALIDA")
            return stock_nuevo
            
        except Exception as e:
            conexion.rollback()
            print(f"❌ Error al actualizar stock: {e}")
            raise e
        finally:
            cursor.close()
            conexion.close()
    
    @staticmethod
    def get_categorias():
        """Obtiene todas las categorías activas"""
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categorias WHERE activo = TRUE ORDER BY nombre")
        rows = cursor.fetchall()
        cursor.close()
        conexion.close()
        categorias = [Categoria.from_dict(row) for row in rows]
        return categorias
    
    @staticmethod
    def get_proveedores():
        """Obtiene todos los proveedores activos"""
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM proveedores WHERE activo = TRUE ORDER BY nombre")
        rows = cursor.fetchall()
        cursor.close()
        conexion.close()
        proveedores = [Proveedor.from_dict(row) for row in rows]
        return proveedores
    
    @staticmethod
    def get_movimientos_producto(id_producto, limite=50):
        """Obtiene el historial de movimientos de un producto específico"""
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT m.*, tm.nombre as tipo_movimiento,
                   CASE 
                       WHEN m.cantidad > 0 THEN 'ENTRADA'
                       ELSE 'SALIDA'
                   END as tipo_operacion
            FROM movimientos_stock m
            JOIN tipos_movimiento tm ON m.id_tipo_movimiento = tm.id_tipo_movimiento
            WHERE m.id_producto = %s
            ORDER BY m.fecha DESC
            LIMIT %s
        """, (id_producto, limite))
        
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
        return resultados