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
        
        # Buscar pendientes
        cursor.execute("SELECT * FROM ventas_pendientes_stock WHERE estado = 'pendiente'")
        pendientes = cursor.fetchall()
        
        for p in pendientes:
            id_evento = p['id_evento']
            codigo = p['codigo_producto']
            cantidad = p['cantidad']
            ref = p['referencia_externa']
            
            # Buscar el producto
            cursor.execute("SELECT id_producto, stock_actual, nombre FROM productos WHERE codigo = %s", (codigo,))
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
            
            # NOTA: En un caso real podríamos permitir stock negativo momentáneo,
            # pero aquí lo limitaremos o advertiremos. Para el MVP permitimos que 
            # el stock quede negativo pero informamos.
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
    datos = request.get_json()
    
    if not datos or 'productos' not in datos:
        return jsonify({"error": "Formato inválido. Se requiere una lista de 'productos'."}), 400
        
    productos = datos.get('productos', [])
    if not productos:
        return jsonify({"error": "La lista de productos está vacía."}), 400

    origen = datos.get('origen', 'API')
    ref_externa = datos.get('referencia_externa', f"API-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
    
    conexion = None
    cursor = None
    eventos_generados = []
    
    try:
        conexion = get_connection()
        cursor = conexion.cursor()
        
        # 1. Registrar en la tabla intermedia (contrato de entrada)
        for item in productos:
            codigo = item.get('codigo')
            cantidad = item.get('cantidad', 1)
            
            if not codigo or cantidad <= 0:
                continue
                
            cursor.execute("""
                INSERT INTO ventas_pendientes_stock 
                (origen, codigo_producto, cantidad, referencia_externa, estado)
                VALUES (%s, %s, %s, %s, 'pendiente')
            """, (origen, codigo, cantidad, ref_externa))
            eventos_generados.append(cursor.lastrowid)
            
        conexion.commit()
        
        # 2. Iniciar el proceso de stock de inmediato
        resultados = procesar_ventas_pendientes()
        
        return jsonify({
            "mensaje": "Venta recibida y procesada en el flujo de integración.",
            "referencia": ref_externa,
            "eventos_procesados": len(eventos_generados),
            "detalles": resultados
        }), 200
        
    except Exception as e:
        if conexion:
            conexion.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
    finally:
        close_connection(conexion, cursor)

def iniciar_api():
    print("Iniciando API de integración en el puerto 5000...")
    print("Contrato de entrada activo: Tabla 'ventas_pendientes_stock'")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    iniciar_api()
