# -*- coding: utf-8 -*-
"""
Script de creación e inicialización de la Base de Datos.

Este módulo se encarga de crear la base de datos `control_stock` desde cero,
definir todas las tablas del sistema (categorías, productos, ventas, pedidos,
roles, usuarios, etc.), insertar los datos iniciales necesarios para el
primer inicio del sistema, y definir la vista de alertas de stock.
"""

import mysql.connector

def crear_base_datos():
    """
    Crea la base de datos 'control_stock', define su esquema y carga datos iniciales.

    Establece una conexión temporal con MySQL Localhost (usando el usuario root),
    elimina la base de datos previa si existe, crea la nueva estructura de tablas,
    agrega relaciones de claves foráneas, inserta registros iniciales
    para roles, usuario administrador por defecto, categorías, proveedores
    y productos de muestra, y finalmente crea la vista `vw_stock_alertas`.

    Raises:
        mysql.connector.Error: Si ocurre algún error en la conexión o ejecución de sentencias SQL.
    """
    try:
        # Conectar sin seleccionar base de datos
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Arcangeles369"
        )
        cursor = conexion.cursor()
        
        # Crear la base de datos
        cursor.execute("DROP DATABASE IF EXISTS control_stock")
        cursor.execute("CREATE DATABASE control_stock")
        cursor.execute("USE control_stock")
        print("✅ Base de datos 'control_stock' creada")
        
        # =====================================================
        # CREAR TABLAS
        # =====================================================
        
        # Tabla categorias
        cursor.execute("""
        CREATE TABLE categorias (
            id_categoria INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) NOT NULL UNIQUE,
            descripcion TEXT,
            activo BOOLEAN DEFAULT TRUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("✅ Tabla categorias creada")
        
        # Tabla proveedores
        cursor.execute("""
        CREATE TABLE proveedores (
            id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            ruc VARCHAR(20),
            telefono VARCHAR(20),
            email VARCHAR(100),
            direccion TEXT,
            contacto_nombre VARCHAR(100),
            contacto_telefono VARCHAR(20),
            activo BOOLEAN DEFAULT TRUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("✅ Tabla proveedores creada")
        
        # Tabla productos
        cursor.execute("""
        CREATE TABLE productos (
            id_producto INT AUTO_INCREMENT PRIMARY KEY,
            codigo VARCHAR(50) NOT NULL UNIQUE,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            id_categoria INT,
            id_proveedor INT,
            precio_compra DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            precio_venta DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            stock_actual INT NOT NULL DEFAULT 0,
            stock_minimo INT NOT NULL DEFAULT 5,
            stock_maximo INT DEFAULT NULL,
            ubicacion VARCHAR(50),
            unidad_medida VARCHAR(20) DEFAULT 'unidad',
            activo BOOLEAN DEFAULT TRUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
            FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
        )
        """)
        print("✅ Tabla productos creada")
        
        # Tabla tipos_movimiento
        cursor.execute("""
        CREATE TABLE tipos_movimiento (
            id_tipo_movimiento INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(30) NOT NULL UNIQUE,
            signo INT NOT NULL,
            descripcion VARCHAR(100)
        )
        """)
        print("✅ Tabla tipos_movimiento creada")
        
        # Tabla movimientos_stock
        cursor.execute("""
        CREATE TABLE movimientos_stock (
            id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
            id_producto INT NOT NULL,
            id_tipo_movimiento INT NOT NULL,
            cantidad INT NOT NULL,
            stock_antes INT NOT NULL,
            stock_despues INT NOT NULL,
            referencia_tipo VARCHAR(50),
            referencia_id INT,
            observacion TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario VARCHAR(50),
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
            FOREIGN KEY (id_tipo_movimiento) REFERENCES tipos_movimiento(id_tipo_movimiento)
        )
        """)
        print("✅ Tabla movimientos_stock creada")
        
        # Tabla estados_venta
        cursor.execute("""
        CREATE TABLE estados_venta (
            id_estado INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(30) NOT NULL UNIQUE
        )
        """)
        print("✅ Tabla estados_venta creada")
        
        # Tabla ventas
        cursor.execute("""
        CREATE TABLE ventas (
            id_venta INT AUTO_INCREMENT PRIMARY KEY,
            numero_factura VARCHAR(20) UNIQUE,
            fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            id_cliente VARCHAR(50) DEFAULT 'CONSUMIDOR FINAL',
            cliente_nombre VARCHAR(100),
            subtotal DECIMAL(10,2) DEFAULT 0.00,
            iva DECIMAL(10,2) DEFAULT 0.00,
            total DECIMAL(10,2) DEFAULT 0.00,
            id_estado INT DEFAULT 1,
            observaciones TEXT,
            usuario VARCHAR(50),
            FOREIGN KEY (id_estado) REFERENCES estados_venta(id_estado)
        )
        """)
        print("✅ Tabla ventas creada")
        
        # Tabla detalles_venta
        cursor.execute("""
        CREATE TABLE detalles_venta (
            id_detalle INT AUTO_INCREMENT PRIMARY KEY,
            id_venta INT NOT NULL,
            id_producto INT NOT NULL,
            cantidad INT NOT NULL,
            precio_unitario DECIMAL(10,2) NOT NULL,
            subtotal DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE,
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        )
        """)
        print("✅ Tabla detalles_venta creada")
        
        # Tabla estados_pedido
        cursor.execute("""
        CREATE TABLE estados_pedido (
            id_estado INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(30) NOT NULL UNIQUE
        )
        """)
        print("✅ Tabla estados_pedido creada")
        
        # Tabla pedidos
        cursor.execute("""
        CREATE TABLE pedidos (
            id_pedido INT AUTO_INCREMENT PRIMARY KEY,
            numero_pedido VARCHAR(20) UNIQUE,
            id_proveedor INT NOT NULL,
            fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_entrega_esperada DATE,
            fecha_entrega_real DATE,
            subtotal DECIMAL(10,2) DEFAULT 0.00,
            iva DECIMAL(10,2) DEFAULT 0.00,
            total DECIMAL(10,2) DEFAULT 0.00,
            id_estado INT DEFAULT 1,
            observaciones TEXT,
            usuario VARCHAR(50),
            FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor),
            FOREIGN KEY (id_estado) REFERENCES estados_pedido(id_estado)
        )
        """)
        print("✅ Tabla pedidos creada")
        
        # Tabla detalles_pedido
        cursor.execute("""
        CREATE TABLE detalles_pedido (
            id_detalle INT AUTO_INCREMENT PRIMARY KEY,
            id_pedido INT NOT NULL,
            id_producto INT NOT NULL,
            cantidad INT NOT NULL,
            cantidad_recibida INT DEFAULT 0,
            precio_unitario DECIMAL(10,2) NOT NULL,
            subtotal DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        )
        """)
        print("✅ Tabla detalles_pedido creada")
        
        # Tabla roles
        cursor.execute("""
        CREATE TABLE roles (
            id_rol INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(30) NOT NULL UNIQUE,
            descripcion VARCHAR(100)
        )
        """)
        print("✅ Tabla roles creada")
        
        # Tabla usuarios
        cursor.execute("""
        CREATE TABLE usuarios (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
            contrasena VARCHAR(255) NOT NULL,
            nombre_completo VARCHAR(100),
            email VARCHAR(100),
            id_rol INT NOT NULL,
            activo BOOLEAN DEFAULT TRUE,
            ultimo_acceso TIMESTAMP NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
        )
        """)
        print("✅ Tabla usuarios creada")
        
        # =====================================================
        # INSERTAR DATOS INICIALES
        # =====================================================
        
        # Tipos de movimiento
        cursor.executemany("""
        INSERT INTO tipos_movimiento (nombre, signo, descripcion) VALUES (%s, %s, %s)
        """, [
            ('Venta', -1, 'Salida por venta'),
            ('Compra', 1, 'Entrada por compra'),
            ('Ajuste_inventario', 1, 'Ajuste manual positivo'),
            ('Ajuste_negativo', -1, 'Ajuste manual negativo'),
            ('Devolucion_venta', 1, 'Devolución de cliente'),
            ('Devolucion_compra', -1, 'Devolución a proveedor'),
            ('Merma', -1, 'Pérdida de producto')
        ])
        print("✅ Datos en tipos_movimiento")
        
        # Estados de venta
        cursor.executemany("""
        INSERT INTO estados_venta (nombre) VALUES (%s)
        """, [('Pendiente',), ('Completada',), ('Cancelada',), ('Devuelta',)])
        print("✅ Datos en estados_venta")
        
        # Estados de pedido
        cursor.executemany("""
        INSERT INTO estados_pedido (nombre) VALUES (%s)
        """, [('Pendiente',), ('Enviado',), ('Recibido',), ('Cancelado',)])
        print("✅ Datos en estados_pedido")
        
        # Roles
        cursor.executemany("""
        INSERT INTO roles (nombre, descripcion) VALUES (%s, %s)
        """, [
            ('Administrador', 'Acceso total al sistema'),
            ('Vendedor', 'Registro de ventas y consultas'),
            ('Encargado_compras', 'Gestión de pedidos y proveedores')
        ])
        print("✅ Datos en roles")
        
        # Usuario admin
        cursor.execute("""
        INSERT INTO usuarios (nombre_usuario, contrasena, nombre_completo, email, id_rol) 
        VALUES (%s, %s, %s, %s, %s)
        """, ('admin', 'admin123', 'Administrador del Sistema', 'admin@controlstock.com', 1))
        print("✅ Usuario admin creado (contraseña: admin123)")
        
        # Categorías
        cursor.executemany("""
        INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)
        """, [
            ('Bebidas', 'Gaseosas, jugos, aguas, cervezas'),
            ('Alimentos', 'Comestibles en general'),
            ('Limpieza', 'Productos de limpieza'),
            ('Perfumería', 'Productos de higiene personal'),
            ('Lácteos', 'Leche, yogures, quesos')
        ])
        print("✅ Datos en categorias")
        
        # Proveedores
        cursor.executemany("""
        INSERT INTO proveedores (nombre, ruc, telefono, email, direccion) VALUES (%s, %s, %s, %s, %s)
        """, [
            ('Distribuidora Sur S.A.', '30-12345678-9', '011-4567-8901', 'ventas@distribuidorasur.com', 'Av. Corrientes 1234, CABA'),
            ('Alimentos del Centro', '30-23456789-0', '011-5678-9012', 'ventas@alimentoscentro.com', 'Av. Rivadavia 5678, CABA'),
            ('Limpieza Total', '30-34567890-1', '011-6789-0123', 'ventas@limpiezatotal.com', 'Av. San Martín 901, CABA')
        ])
        print("✅ Datos en proveedores")
        
        # Productos
        cursor.executemany("""
        INSERT INTO productos (codigo, nombre, id_categoria, id_proveedor, precio_compra, precio_venta, stock_actual, stock_minimo) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, [
            ('CO001', 'Coca Cola 2L', 1, 1, 180.00, 250.00, 50, 10),
            ('CO002', 'Sprite 2L', 1, 1, 170.00, 240.00, 30, 10),
            ('CO003', 'Agua Mineral 500ml', 1, 1, 80.00, 120.00, 100, 20),
            ('AL001', 'Arroz 1kg', 2, 2, 120.00, 180.00, 40, 15),
            ('AL002', 'Fideos 500g', 2, 2, 90.00, 140.00, 25, 10),
            ('AL003', 'Aceite 900ml', 2, 2, 200.00, 300.00, 8, 10),
            ('LM001', 'Detergente 500ml', 3, 3, 150.00, 220.00, 5, 10),
            ('LM002', 'Lavandina 1L', 3, 3, 80.00, 130.00, 35, 15),
            ('PF001', 'Shampoo 400ml', 4, 3, 250.00, 380.00, 12, 5),
            ('LA001', 'Leche Entera 1L', 5, 2, 110.00, 170.00, 3, 10)
        ])
        print("✅ Datos en productos")
        
        # Crear vista de alertas de stock
        cursor.execute("""
        CREATE OR REPLACE VIEW vw_stock_alertas AS
        SELECT 
            p.id_producto,
            p.codigo,
            p.nombre,
            c.nombre AS categoria,
            p.stock_actual,
            p.stock_minimo,
            CASE 
                WHEN p.stock_actual <= 0 THEN 'SIN STOCK'
                WHEN p.stock_actual <= p.stock_minimo THEN 'STOCK BAJO'
                ELSE 'NORMAL'
            END AS estado_stock,
            GREATEST(0, p.stock_minimo - p.stock_actual) AS cantidad_recomendada,
            pr.nombre AS proveedor
        FROM productos p
        LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
        LEFT JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
        WHERE p.activo = TRUE
        """)
        print("✅ Vista vw_stock_alertas creada")
        
        conexion.commit()
        print("\n" + "="*50)
        print("🎉 BASE DE DATOS CREADA EXITOSAMENTE!")
        print("="*50)
        print("Usuario: admin")
        print("Contraseña: admin123")
        print("="*50)
        
        cursor.close()
        conexion.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    crear_base_datos()