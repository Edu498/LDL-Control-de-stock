-- =====================================================
-- SISTEMA DE CONTROL DE STOCK
-- Base de datos: control_stock
-- =====================================================

-- Crear la base de datos
DROP DATABASE IF EXISTS control_stock;
CREATE DATABASE control_stock;
USE control_stock;

-- =====================================================
-- 1. TABLAS PRINCIPALES
-- =====================================================

-- Tabla de categorías
CREATE TABLE categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de proveedores
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
);

-- Tabla de productos (principal)
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
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor),
    INDEX idx_codigo (codigo),
    INDEX idx_nombre (nombre),
    INDEX idx_stock (stock_actual, stock_minimo)
);

-- =====================================================
-- 2. TABLAS DE MOVIMIENTOS DE STOCK
-- =====================================================

-- Tipos de movimiento de stock
CREATE TABLE tipos_movimiento (
    id_tipo_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE,
    signo INT NOT NULL COMMENT '1=entrada, -1=salida',
    descripcion VARCHAR(100)
);

-- Insertar tipos de movimiento
INSERT INTO tipos_movimiento (nombre, signo, descripcion) VALUES
('Venta', -1, 'Salida por venta'),
('Compra', 1, 'Entrada por compra'),
('Ajuste_inventario', 1, 'Ajuste manual positivo'),
('Ajuste_negativo', -1, 'Ajuste manual negativo'),
('Devolucion_venta', 1, 'Devolución de cliente'),
('Devolucion_compra', -1, 'Devolución a proveedor'),
('Merma', -1, 'Pérdida de producto');

-- Registro de movimientos de stock (historial)
CREATE TABLE movimientos_stock (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    id_tipo_movimiento INT NOT NULL,
    cantidad INT NOT NULL,
    stock_antes INT NOT NULL,
    stock_despues INT NOT NULL,
    referencia_tipo VARCHAR(50) COMMENT 'venta, compra, ajuste',
    referencia_id INT COMMENT 'ID del documento relacionado',
    observacion TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario VARCHAR(50),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_tipo_movimiento) REFERENCES tipos_movimiento(id_tipo_movimiento),
    INDEX idx_producto (id_producto),
    INDEX idx_fecha (fecha)
);

-- =====================================================
-- 3. TABLAS DE VENTAS
-- =====================================================

-- Estado de ventas
CREATE TABLE estados_venta (
    id_estado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE
);

INSERT INTO estados_venta (nombre) VALUES
('Pendiente'), ('Completada'), ('Cancelada'), ('Devuelta');

-- Cabecera de ventas
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
    FOREIGN KEY (id_estado) REFERENCES estados_venta(id_estado),
    INDEX idx_fecha (fecha_venta),
    INDEX idx_numero (numero_factura)
);

-- Detalle de ventas
CREATE TABLE detalles_venta (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    INDEX idx_venta (id_venta),
    INDEX idx_producto (id_producto)
);

-- =====================================================
-- 4. TABLAS DE COMPRAS Y PEDIDOS
-- =====================================================

-- Estado de pedidos
CREATE TABLE estados_pedido (
    id_estado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE
);

INSERT INTO estados_pedido (nombre) VALUES
('Pendiente'), ('Enviado'), ('Recibido'), ('Cancelado');

-- Cabecera de pedidos a proveedores
CREATE TABLE pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    numero_pedido VARCHAR(30) UNIQUE,
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
    FOREIGN KEY (id_estado) REFERENCES estados_pedido(id_estado),
    INDEX idx_fecha (fecha_pedido)
);

-- Detalle de pedidos
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
);

-- =====================================================
-- 5. TABLAS DE CONTROL FÍSICO DE INVENTARIO
-- =====================================================

-- Conteos físicos de inventario
CREATE TABLE conteos_inventario (
    id_conteo INT AUTO_INCREMENT PRIMARY KEY,
    fecha_conteo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    descripcion VARCHAR(200),
    usuario VARCHAR(50),
    cerrado BOOLEAN DEFAULT FALSE
);

-- Detalle del conteo físico
CREATE TABLE detalles_conteo (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_conteo INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad_sistema INT NOT NULL,
    cantidad_fisica INT NOT NULL,
    diferencia INT NOT NULL,
    observacion TEXT,
    FOREIGN KEY (id_conteo) REFERENCES conteos_inventario(id_conteo) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- =====================================================
-- 6. TABLAS DE USUARIOS Y ROLES
-- =====================================================

-- Roles de usuario
CREATE TABLE roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE,
    descripcion VARCHAR(100)
);

INSERT INTO roles (nombre, descripcion) VALUES
('Administrador', 'Acceso total al sistema'),
('Vendedor', 'Registro de ventas y consultas'),
('Encargado_compras', 'Gestión de pedidos y proveedores');

-- Usuarios del sistema
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
);

-- Insertar usuario administrador por defecto (contraseña: admin123)
INSERT INTO usuarios (nombre_usuario, contrasena, nombre_completo, id_rol, activo) 
VALUES ('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Administrador Principal', 1, TRUE);

-- =====================================================
-- 7. VISTAS ÚTILES
-- =====================================================

-- Vista de stock actual con alertas
CREATE VIEW vw_stock_alertas AS
SELECT 
    p.id_producto,
    p.codigo,
    p.nombre,
    c.nombre AS categoria,
    p.stock_actual,
    p.stock_minimo,
    CASE 
        WHEN p.stock_actual <= 0 THEN 'SIN STOCK'
        WHEN p.stock_actual < p.stock_minimo THEN 'STOCK BAJO'
        ELSE 'NORMAL'
    END AS estado_stock,
    (p.stock_minimo - p.stock_actual) AS cantidad_recomendada,
    pr.nombre AS proveedor
FROM productos p
LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
LEFT JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
WHERE p.activo = TRUE;

-- Vista de productos más vendidos
CREATE VIEW vw_productos_mas_vendidos AS
SELECT 
    p.id_producto,
    p.codigo,
    p.nombre,
    SUM(dv.cantidad) AS total_vendido,
    COUNT(DISTINCT dv.id_venta) AS numero_ventas,
    SUM(dv.subtotal) AS ingreso_total
FROM detalles_venta dv
JOIN productos p ON dv.id_producto = p.id_producto
JOIN ventas v ON dv.id_venta = v.id_venta
WHERE v.id_estado = 2 -- Completadas
GROUP BY p.id_producto
ORDER BY total_vendido DESC;

-- =====================================================
-- 8. PROCEDIMIENTOS ALMACENADOS
-- =====================================================

-- Procedimiento para registrar venta y actualizar stock
DELIMITER //
CREATE PROCEDURE sp_registrar_venta(
    IN p_cliente_nombre VARCHAR(100),
    IN p_productos_json JSON,
    IN p_usuario VARCHAR(50)
)
BEGIN
    DECLARE v_id_venta INT;
    DECLARE v_total DECIMAL(10,2) DEFAULT 0;
    DECLARE v_i INT DEFAULT 0;
    DECLARE v_cantidad INT;
    DECLARE v_precio DECIMAL(10,2);
    DECLARE v_id_producto INT;
    DECLARE v_stock_actual INT;
    
    -- Iniciar transacción
    START TRANSACTION;
    
    -- Insertar cabecera de venta
    INSERT INTO ventas (cliente_nombre, fecha_venta, usuario, id_estado)
    VALUES (p_cliente_nombre, NOW(), p_usuario, 1);
    
    SET v_id_venta = LAST_INSERT_ID();
    
    -- Procesar productos
    WHILE v_i < JSON_LENGTH(p_productos_json) DO
        SET v_id_producto = JSON_EXTRACT(p_productos_json, CONCAT('$[', v_i, '].id_producto'));
        SET v_cantidad = JSON_EXTRACT(p_productos_json, CONCAT('$[', v_i, '].cantidad'));
        SET v_precio = JSON_EXTRACT(p_productos_json, CONCAT('$[', v_i, '].precio'));
        
        -- Verificar stock
        SELECT stock_actual INTO v_stock_actual FROM productos WHERE id_producto = v_id_producto;
        
        IF v_stock_actual < v_cantidad THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente';
        END IF;
        
        -- Insertar detalle
        INSERT INTO detalles_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal)
        VALUES (v_id_venta, v_id_producto, v_cantidad, v_precio, v_cantidad * v_precio);
        
        -- Actualizar stock
        UPDATE productos 
        SET stock_actual = stock_actual - v_cantidad 
        WHERE id_producto = v_id_producto;
        
        -- Registrar movimiento
        INSERT INTO movimientos_stock (id_producto, id_tipo_movimiento, cantidad, stock_antes, stock_despues, referencia_tipo, referencia_id)
        VALUES (v_id_producto, 1, -v_cantidad, v_stock_actual, v_stock_actual - v_cantidad, 'venta', v_id_venta);
        
        SET v_total = v_total + (v_cantidad * v_precio);
        SET v_i = v_i + 1;
    END WHILE;
    
    -- Actualizar totales
    UPDATE ventas SET total = v_total WHERE id_venta = v_id_venta;
    
    COMMIT;
    
    SELECT v_id_venta AS id_venta;
END//
DELIMITER ;

-- Procedimiento para generar pedido automático por stock bajo
DELIMITER //
CREATE PROCEDURE sp_generar_pedido_automatico()
BEGIN
    DECLARE v_id_pedido INT;
    
    -- Crear pedido para productos con stock bajo
    INSERT INTO pedidos (numero_pedido, id_proveedor, fecha_pedido, observaciones, id_estado)
    SELECT 
        CONCAT('AUTO-', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s')),
        id_proveedor,
        NOW(),
        CONCAT('Pedido automático por stock bajo - ', COUNT(*) , ' productos'),
        1
    FROM vw_stock_alertas 
    WHERE estado_stock IN ('STOCK BAJO', 'SIN STOCK') 
    AND proveedor IS NOT NULL
    GROUP BY id_proveedor;
    
    SET v_id_pedido = LAST_INSERT_ID();
    
    -- Agregar productos al pedido
    INSERT INTO detalles_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
    SELECT 
        v_id_pedido,
        id_producto,
        cantidad_recomendada,
        p.precio_compra,
        cantidad_recomendada * p.precio_compra
    FROM vw_stock_alertas sa
    JOIN productos p ON sa.id_producto = p.id_producto
    WHERE estado_stock IN ('STOCK BAJO', 'SIN STOCK');
    
    SELECT v_id_pedido AS id_pedido;
END//
DELIMITER ;

-- =====================================================
-- 9. DATOS DE PRUEBA
-- =====================================================

-- Categorías de prueba
INSERT INTO categorias (nombre, descripcion) VALUES
('Bebidas', 'Gaseosas, jugos, aguas, cervezas'),
('Alimentos', 'Comestibles en general'),
('Limpieza', 'Productos de limpieza'),
('Perfumería', 'Productos de higiene personal'),
('Lácteos', 'Leche, yogures, quesos'),
('Fiambres', 'Jamón, queso, salamines'),
('Panadería', 'Panes, facturas, tortas');

-- Proveedores de prueba
INSERT INTO proveedores (nombre, ruc, telefono, email, direccion) VALUES
('Distribuidora Sur S.A.', '30-12345678-9', '011-4567-8901', 'ventas@distribuidorasur.com', 'Av. Corrientes 1234, CABA'),
('Alimentos del Centro', '30-23456789-0', '011-5678-9012', 'ventas@alimentoscentro.com', 'Av. Rivadavia 5678, CABA'),
('Limpieza Total', '30-34567890-1', '011-6789-0123', 'ventas@limpiezatotal.com', 'Av. San Martín 901, CABA');

-- Productos de prueba
INSERT INTO productos (codigo, nombre, id_categoria, id_proveedor, precio_compra, precio_venta, stock_actual, stock_minimo) VALUES
('CO001', 'Coca Cola 2L', 1, 1, 180.00, 250.00, 50, 10),
('CO002', 'Sprite 2L', 1, 1, 170.00, 240.00, 30, 10),
('CO003', 'Agua Mineral 500ml', 1, 1, 80.00, 120.00, 100, 20),
('AL001', 'Arroz 1kg', 2, 2, 120.00, 180.00, 40, 15),
('AL002', 'Fideos 500g', 2, 2, 90.00, 140.00, 25, 10),
('AL003', 'Aceite 900ml', 2, 2, 200.00, 300.00, 15, 8),
('LM001', 'Detergente 500ml', 3, 3, 150.00, 220.00, 20, 10),
('LM002', 'Lavandina 1L', 3, 3, 80.00, 130.00, 35, 15),
('PF001', 'Shampoo 400ml', 4, 3, 250.00, 380.00, 12, 5),
('PF002', 'Jabón íntimo', 4, 3, 180.00, 280.00, 18, 8),
('LA001', 'Leche Entera 1L', 5, 2, 110.00, 170.00, 8, 10),  -- Stock bajo!
('LA002', 'Yogur Firme 200g', 5, 2, 80.00, 130.00, 3, 8),    -- Stock bajo!
('FI001', 'Jamón Cocido 500g', 6, 2, 400.00, 580.00, 5, 6),    -- Stock bajo!
('PA001', 'Pan Francés', 7, NULL, 50.00, 80.00, 0, 10);       -- Sin stock!

-- =====================================================
-- 10. CONSULTAS ÚTILES PARA EL SISTEMA
-- =====================================================

-- Productos con alertas de stock
SELECT * FROM vw_stock_alertas 
WHERE estado_stock != 'NORMAL'
ORDER BY estado_stock, stock_actual;

-- Productos que necesitan reposición urgente
SELECT 
    p.nombre,
    p.stock_actual,
    p.stock_minimo,
    (p.stock_minimo - p.stock_actual) AS cantidad_faltante,
    pr.nombre AS proveedor
FROM productos p
LEFT JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
WHERE p.stock_actual <= p.stock_minimo
ORDER BY (p.stock_minimo - p.stock_actual) DESC;

-- Ventas del día
SELECT 
    COUNT(*) AS total_ventas,
    SUM(total) AS monto_total,
    COUNT(DISTINCT id_venta) AS numero_ventas
FROM ventas
WHERE DATE(fecha_venta) = CURDATE()
AND id_estado = 2;

-- Productos más vendidos del mes
SELECT * FROM vw_productos_mas_vendidos
LIMIT 10;

-- Movimientos de stock de un producto específico
SELECT 
    m.*,
    p.nombre AS producto,
    tm.nombre AS tipo_movimiento
FROM movimientos_stock m
JOIN productos p ON m.id_producto = p.id_producto
JOIN tipos_movimiento tm ON m.id_tipo_movimiento = tm.id_tipo_movimiento
WHERE m.id_producto = 1
ORDER BY m.fecha DESC
LIMIT 20;

-- =====================================================
-- 11. ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- =====================================================

CREATE INDEX idx_productos_stock ON productos(stock_actual, stock_minimo);
CREATE INDEX idx_ventas_fecha ON ventas(fecha_venta);
CREATE INDEX idx_movimientos_producto ON movimientos_stock(id_producto, fecha);
CREATE INDEX idx_pedidos_estado ON pedidos(id_estado, fecha_pedido);

