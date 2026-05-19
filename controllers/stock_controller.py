import mysql.connector
from models import Producto, Categoria, Proveedor
from utils.database import get_connection

class StockController:
    @staticmethod
    def get_all_productos():
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
        conexion = get_connection()
        cursor = conexion.cursor()
        
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
        
        cursor.close()
        conexion.close()
        return producto
    
    @staticmethod
    def actualizar_stock(id_producto, cantidad, tipo_movimiento, usuario, referencia=None):
        conexion = get_connection()
        cursor = conexion.cursor()
        
        # Obtener stock actual
        cursor.execute("SELECT stock_actual FROM productos WHERE id_producto = %s", (id_producto,))
        stock_actual = cursor.fetchone()[0]
        
        stock_nuevo = stock_actual + cantidad
        
        # Actualizar producto
        cursor.execute("UPDATE productos SET stock_actual = %s WHERE id_producto = %s", 
                      (stock_nuevo, id_producto))
        
        # Registrar movimiento
        cursor.execute("""
            INSERT INTO movimientos_stock (id_producto, id_tipo_movimiento, cantidad, 
                                           stock_antes, stock_despues, referencia_tipo, 
                                           referencia_id, usuario)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (id_producto, tipo_movimiento, cantidad, stock_actual, stock_nuevo,
              referencia.get('tipo') if referencia else None,
              referencia.get('id') if referencia else None, usuario))
        
        conexion.commit()
        cursor.close()
        conexion.close()
        
        return stock_nuevo
    
    @staticmethod
    def get_categorias():
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categorias WHERE activo = TRUE ORDER BY nombre")
        categorias = [Categoria(**row) for row in cursor.fetchall()]
        cursor.close()
        conexion.close()
        return categorias
    
    @staticmethod
    def get_proveedores():
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM proveedores WHERE activo = TRUE ORDER BY nombre")
        proveedores = [Proveedor(**row) for row in cursor.fetchall()]
        cursor.close()
        conexion.close()
        return proveedores