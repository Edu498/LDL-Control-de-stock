import mysql.connector
from models import Producto, Categoria, Proveedor
from utils.database import get_connection, execute_query, close_connection

class StockController:
    """Controlador profesional para gestión de stock"""
    
    @staticmethod
    def get_all_productos():
        """Obtiene todos los productos activos con sus relaciones"""
        
        query = """
            SELECT p.*, c.nombre as categoria_nombre, pr.nombre as proveedor_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
            LEFT JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
            WHERE p.activo = TRUE
            ORDER BY p.nombre
        """
        rows = execute_query(query, fetch_all=True)
        
        productos = []
        if rows:
            for row in rows:
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
        return productos
    
    @staticmethod
    def get_productos_con_alerta():
        """Obtiene productos con stock crítico (bajo o sin stock)"""
        query = """
            SELECT * FROM vw_stock_alertas
            WHERE stock_actual <= stock_minimo
            ORDER BY 
                (stock_actual <= 0) DESC, 
                stock_actual ASC
        """
        return execute_query(query, fetch_all=True)
    
    @staticmethod
    def get_producto_by_id(id_producto):
        """Obtiene un producto específico por su ID"""
        
        query = "SELECT * FROM productos WHERE id_producto = %s"
        row = execute_query(query, params=(id_producto,), fetch_one=True)
        
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
            if conexion:
                conexion.rollback()
            raise e
        finally:
            close_connection(conexion, cursor)
    
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
        
        conexion = None
        cursor = None
        
        try:
            conexion = get_connection()
            cursor = conexion.cursor()
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
            if conexion:
                conexion.rollback()
            print(f"❌ Error al actualizar stock: {e}")
            raise e
        finally:
            close_connection(conexion, cursor)
    
    @staticmethod
    def get_categorias():
        """Obtiene todas las categorías activas"""
        rows = execute_query("SELECT * FROM categorias WHERE activo = TRUE ORDER BY nombre", fetch_all=True)
        return [Categoria.from_dict(row) for row in rows] if rows else []
    
    @staticmethod
    def get_proveedores():
        """Obtiene todos los proveedores activos"""
        rows = execute_query("SELECT * FROM proveedores WHERE activo = TRUE ORDER BY nombre", fetch_all=True)
        return [Proveedor.from_dict(row) for row in rows] if rows else []
    
    @staticmethod
    def get_movimientos_producto(id_producto, limite=50):
        """Obtiene el historial de movimientos de un producto específico"""
        query = """
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
        """
        return execute_query(query, params=(id_producto, limite), fetch_all=True)