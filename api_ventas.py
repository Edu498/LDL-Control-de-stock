from flask import Flask, request, jsonify
from utils.database import get_connection, close_connection
import datetime

app = Flask(__name__)

def procesar_ventas_pendientes():
    """
    Función que lee la tabla ventas_pendientes_stock buscando registros en estado 'pendiente'.
    Si el stock es suficiente, lo descuenta y marca como 'procesada'.
    Si falla (ej. sin stock o producto inexistente), marca como 'error' con el mensaje correspondiente.
    """
    conexion = None
    cursor = None
    resultados = []
    
    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        # Iniciar transacción
        conexion.start_transaction()
        
        # Buscar pendientes y bloquear las filas para evitar concurrencia
        cursor.execute("SELECT * FROM ventas_pendientes_stock WHERE estado = 'pendiente' FOR UPDATE")
        pendientes = cursor.fetchall()
        
        for p in pendientes:
            id_evento = p['id_evento']
            codigo = p['codigo_producto']
            cantidad = p['cantidad']
            ref = p['referencia_externa']
            
            # Buscar el producto y bloquear la fila para evitar conflictos de stock
            cursor.execute("SELECT id_producto, stock_actual, nombre FROM productos WHERE codigo = %s FOR UPDATE", (codigo,))
            producto = cursor.fetchone()
            
            if not producto:
                # Marcar error
                cursor.execute("""
                    UPDATE ventas_pendientes_stock 
                    SET estado = 'error', mensaje_error = 'Producto no encontrado', fecha_procesado = NOW() 
                    WHERE id_evento = %s
                """, (id_evento,))
                resultados.append({"id_evento": id_evento, "status": "error", "mensaje": "Producto no encontrado"})
                continue
                
            id_prod = producto['id_producto']
            stock_antes = producto['stock_actual']
            
            if stock_antes < cantidad:
                # Marcar error por falta de stock
                cursor.execute("""
                    UPDATE ventas_pendientes_stock 
                    SET estado = 'error', mensaje_error = 'Stock insuficiente', fecha_procesado = NOW() 
                    WHERE id_evento = %s
                """, (id_evento,))
                resultados.append({
                    "id_evento": id_evento, 
                    "codigo": codigo,
                    "status": "error", 
                    "mensaje": f"Stock insuficiente para procesar la cantidad solicitada ({cantidad})"
                })
                continue
                
            stock_despues = stock_antes - cantidad
            
            # Actualizar stock
            cursor.execute("UPDATE productos SET stock_actual = %s WHERE id_producto = %s", (stock_despues, id_prod))
            
            # Generar movimiento auditado (id_tipo_movimiento = 1 para Venta)
            cursor.execute("""
                INSERT INTO movimientos_stock 
                    (id_producto, id_tipo_movimiento, cantidad, stock_antes, stock_despues, 
                     referencia_tipo, referencia_id, observacion, usuario, fecha)
                VALUES (%s, 1, %s, %s, %s, 'api_integracion', %s, %s, %s, NOW())
            """, (id_prod, cantidad, stock_antes, stock_despues, 
                  id_evento, f"Venta externa integrada (Ref: {ref})", "api_system"))
            
            # Marcar como procesado
            cursor.execute("""
                UPDATE ventas_pendientes_stock 
                SET estado = 'procesada', fecha_procesado = NOW() 
                WHERE id_evento = %s
            """, (id_evento,))
            
            resultados.append({
                "id_evento": id_evento,
                "codigo": codigo,
                "nombre": producto['nombre'],
                "cantidad_descontada": cantidad,
                "stock_restante": stock_despues,
                "status": "success"
            })
            
        conexion.commit()
        return resultados
        
    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"Error procesando ventas: {e}")
        return []
    finally:
        close_connection(conexion, cursor)


@app.route('/api/ventas', methods=['POST'])
def registrar_venta_externa():
    """
    Endpoint para recibir ventas de un sistema externo.
    Formato esperado (JSON):
    {
        "origen": "SISTEMA_POS",
        "referencia_externa": "TX-9988",
        "productos": [
            {"codigo": "CO001", "cantidad": 2},
            {"codigo": "AL001", "cantidad": 1}
        ]
    }
    """
    # Usar silent=True para evitar que Flask aborte si no es un JSON válido
    datos = request.get_json(silent=True)
    
    if not datos:
        return jsonify({"error": "No se recibió un JSON válido o el Content-Type no es application/json."}), 400

    if 'productos' not in datos or not isinstance(datos['productos'], list):
        return jsonify({"error": "Formato inválido. Se requiere una lista de 'productos'."}), 400
        
    productos = datos['productos']
    if len(productos) == 0:
        return jsonify({"error": "La lista de productos está vacía."}), 400
        
    # Validar la estructura de cada producto antes de abrir transacciones en BD
    for item in productos:
        if not isinstance(item, dict):
            return jsonify({"error": "Cada item en 'productos' debe ser un objeto JSON."}), 400
        if 'codigo' not in item or not isinstance(item['codigo'], str) or not item['codigo'].strip():
            return jsonify({"error": "Todos los productos deben tener un 'codigo' válido."}), 400
        
        try:
            cantidad = int(item.get('cantidad', 1))
            if cantidad <= 0:
                return jsonify({"error": f"La cantidad para el producto {item['codigo']} debe ser mayor a 0."}), 400
            item['cantidad'] = cantidad # Normalizar a entero
        except (ValueError, TypeError):
            return jsonify({"error": f"La cantidad para el producto {item['codigo']} debe ser un número entero."}), 400

    origen = datos.get('origen', 'API')
    ref_externa = datos.get('referencia_externa', f"API-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
    
    conexion = None
    cursor = None
    
    try:
        conexion = get_connection()
        
        # Agrupar cantidades por producto para la validación y evitar duplicados
        cantidades_solicitadas = {}
        for item in productos:
            codigo = item['codigo']
            cantidades_solicitadas[codigo] = cantidades_solicitadas.get(codigo, 0) + item['cantidad']

        # Extraer el cliente de los datos o usar uno por defecto basado en el origen
        cliente_nombre = datos.get('cliente', f"API - {origen}")

        # Iniciar transacción
        conexion.start_transaction()
        cursor_dict = conexion.cursor(dictionary=True)
        
        errores = []
        productos_procesar = []
        
        # 1. Validar existencia y stock de todos los productos primero
        for codigo, cantidad in cantidades_solicitadas.items():
            cursor_dict.execute("SELECT id_producto, stock_actual, nombre, precio_venta FROM productos WHERE codigo = %s FOR UPDATE", (codigo,))
            prod_db = cursor_dict.fetchone()
            
            if not prod_db:
                errores.append({"codigo": codigo, "mensaje": f"Producto '{codigo}' no encontrado."})
            elif prod_db['stock_actual'] < cantidad:
                errores.append({"codigo": codigo, "mensaje": f"Stock insuficiente para '{prod_db['nombre']}' (Cantidad solicitada: {cantidad})"})
            else:
                productos_procesar.append({
                    'codigo': codigo,
                    'cantidad': cantidad,
                    'id_producto': prod_db['id_producto'],
                    'nombre': prod_db['nombre'],
                    'stock_actual': prod_db['stock_actual'],
                    'precio_venta': prod_db['precio_venta']
                })
                
        # 2. Si hay errores, cancelar la transacción y devolver Error 400
        if errores:
            conexion.rollback()
            
            # Opcional: Dejar registro en ventas_pendientes_stock como fallido
            cursor_log = conexion.cursor()
            for codigo, cantidad in cantidades_solicitadas.items():
                cursor_log.execute("""
                    INSERT INTO ventas_pendientes_stock 
                    (origen, codigo_producto, cantidad, referencia_externa, estado, mensaje_error, fecha_procesado)
                    VALUES (%s, %s, %s, %s, 'error', 'Venta rechazada en bloque (error de validación)', NOW())
                """, (origen, codigo, cantidad, ref_externa))
            conexion.commit()
            
            return jsonify({
                "mensaje": "La venta fue rechazada por completo.",
                "referencia": ref_externa,
                "detalles": errores
            }), 400

        # 3. Si todo es correcto, crear la cabecera de la venta en la base de datos principal
        cursor = conexion.cursor()
        
        # Calcular totales
        subtotal = sum(p['cantidad'] * float(p['precio_venta']) for p in productos_procesar)
        iva = subtotal * 0.21
        total = subtotal + iva
        
        # Guardar en la tabla de ventas principal
        cursor.execute("""
            INSERT INTO ventas (numero_factura, cliente_nombre, subtotal, iva, total, usuario, id_estado, fecha_venta)
            VALUES (%s, %s, %s, %s, %s, %s, 2, NOW())
        """, (ref_externa, cliente_nombre, subtotal, iva, total, "api_system"))
        
        id_venta_db = cursor.lastrowid
        
        detalles_exito = []
        
        for p in productos_procesar:
            # Registrar detalle en la tabla detalles_venta
            subtotal_item = p['cantidad'] * float(p['precio_venta'])
            cursor.execute("""
                INSERT INTO detalles_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_venta_db, p['id_producto'], p['cantidad'], p['precio_venta'], subtotal_item))
            
            # Registrar en tabla intermedia como procesada
            cursor.execute("""
                INSERT INTO ventas_pendientes_stock 
                (origen, codigo_producto, cantidad, referencia_externa, estado, fecha_procesado)
                VALUES (%s, %s, %s, %s, 'procesada', NOW())
            """, (origen, p['codigo'], p['cantidad'], ref_externa))
            id_evento = cursor.lastrowid
            
            # Descontar stock
            stock_despues = p['stock_actual'] - p['cantidad']
            cursor.execute("UPDATE productos SET stock_actual = %s WHERE id_producto = %s", (stock_despues, p['id_producto']))
            
            # Registrar movimiento de stock (cantidad en NEGATIVO porque es SALIDA)
            cursor.execute("""
                INSERT INTO movimientos_stock 
                    (id_producto, id_tipo_movimiento, cantidad, stock_antes, stock_despues, 
                     referencia_tipo, referencia_id, observacion, usuario, fecha)
                VALUES (%s, 1, %s, %s, %s, 'api_integracion', %s, %s, %s, NOW())
            """, (p['id_producto'], -p['cantidad'], p['stock_actual'], stock_despues, 
                  id_evento, f"Venta externa integrada (Ref: {ref_externa})", "api_system"))
                  
            detalles_exito.append({
                "codigo": p['codigo'],
                "nombre": p['nombre'],
                "cantidad_descontada": p['cantidad'],
                "stock_restante": stock_despues,
                "status": "success",
                "id_evento": id_evento
            })
            
        conexion.commit()
        
        return jsonify({
            "mensaje": "Venta recibida y procesada exitosamente.",
            "referencia": ref_externa,
            "eventos_procesados": len(productos_procesar),
            "detalles": detalles_exito
        }), 200
        
    except Exception as e:
        if conexion:
            conexion.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
    finally:
        close_connection(conexion, cursor)

@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    """
    Endpoint para consultar los productos activos y su stock.
    Permite a sistemas externos (como la vista de ventas) listar el catálogo.
    """
    conexion = None
    cursor = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)
        query = """
            SELECT p.*, c.nombre as categoria_nombre, pr.nombre as proveedor_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
            LEFT JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
            WHERE p.activo = TRUE
            ORDER BY p.nombre
        """
        cursor.execute(query)
        productos = cursor.fetchall()
        
        # Convertir Decimals a float para que sea serializable a JSON y ocultar stock
        for p in productos:
            if 'stock_actual' in p:
                del p['stock_actual']
            if 'stock_minimo' in p:
                del p['stock_minimo']
            if 'stock_maximo' in p:
                del p['stock_maximo']
            
            if p.get('precio_compra') is not None:
                p['precio_compra'] = float(p['precio_compra'])
            if p.get('precio_venta') is not None:
                p['precio_venta'] = float(p['precio_venta'])
            
        return jsonify(productos), 200
    except Exception as e:
        print(f"Error obteniendo productos: {e}")
        return jsonify({"error": "Error interno al obtener productos"}), 500
    finally:
        close_connection(conexion, cursor)

def iniciar_api():
    print("Iniciando API de integración en el puerto 5000...")
    print("Contrato de entrada activo: Tabla 'ventas_pendientes_stock'")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    iniciar_api()
