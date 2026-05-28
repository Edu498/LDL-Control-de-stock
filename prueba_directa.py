# prueba_directa.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.database import get_connection
from controllers.stock_controller import StockController

def probar_agregar_stock():
    print("=" * 60)
    print("PRUEBA DIRECTA - AGREGAR STOCK (ENTRADA)")
    print("=" * 60)
    
    try:
        # Obtener un producto
        productos = StockController.get_all_productos()
        if not productos:
            print("No hay productos")
            return
        
        producto = productos[0]
        print(f"\n📦 Producto: {producto.nombre}")
        print(f"📊 Stock actual: {producto.stock_actual}")
        
        # AGREGAR 5 unidades (CANTIDAD POSITIVA)
        cantidad = 5
        print(f"\n🔧 Agregando {cantidad} unidades (cantidad POSITIVA = +{cantidad})...")
        
        nuevo_stock = StockController.actualizar_stock(
            id_producto=producto.id_producto,
            cantidad=cantidad,      # POSITIVO para ENTRADA
            tipo_movimiento=3,       # Ajuste Positivo
            usuario="prueba_directa",
            referencia={'tipo': 'test', 'motivo': 'Prueba de ENTRADA'}
        )
        
        print(f"\n✅ RESULTADO:")
        print(f"   Stock anterior: {producto.stock_actual}")
        print(f"   Stock nuevo: {nuevo_stock}")
        print(f"   Cantidad registrada: +{cantidad}")
        print(f"   ✅ Esto debería aparecer como ENTRADA en el reporte")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def probar_quitar_stock():
    print("=" * 60)
    print("PRUEBA DIRECTA - QUITAR STOCK (SALIDA)")
    print("=" * 60)
    
    try:
        # Obtener un producto con stock > 0
        productos = StockController.get_all_productos()
        if not productos:
            print("No hay productos")
            return
        
        producto = None
        for p in productos:
            if p.stock_actual > 0:
                producto = p
                break
        
        if not producto:
            print("No hay productos con stock disponible")
            return
        
        print(f"\n📦 Producto: {producto.nombre}")
        print(f"📊 Stock actual: {producto.stock_actual}")
        
        # QUITAR 1 unidad (CANTIDAD NEGATIVA)
        cantidad = -1
        print(f"\n🔧 Quitando 1 unidad (cantidad NEGATIVA = {cantidad})...")
        
        nuevo_stock = StockController.actualizar_stock(
            id_producto=producto.id_producto,
            cantidad=cantidad,      # NEGATIVO para SALIDA
            tipo_movimiento=4,       # Ajuste Negativo
            usuario="prueba_directa",
            referencia={'tipo': 'test', 'motivo': 'Prueba de SALIDA'}
        )
        
        print(f"\n✅ RESULTADO:")
        print(f"   Stock anterior: {producto.stock_actual}")
        print(f"   Stock nuevo: {nuevo_stock}")
        print(f"   Cantidad registrada: {cantidad}")
        print(f"   ✅ Esto debería aparecer como SALIDA en el reporte")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def verificar_ultimo_movimiento():
    print("\n" + "=" * 60)
    print("VERIFICAR ÚLTIMO MOVIMIENTO EN BD")
    print("=" * 60)
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT m.cantidad, m.id_tipo_movimiento, m.stock_antes, m.stock_despues,
                   p.nombre as producto, m.fecha,
                   CASE WHEN m.cantidad > 0 THEN 'ENTRADA' ELSE 'SALIDA' END as tipo
            FROM movimientos_stock m
            JOIN productos p ON m.id_producto = p.id_producto
            ORDER BY m.id_movimiento DESC
            LIMIT 1
        """)
        
        ultimo = cursor.fetchone()
        if ultimo:
            print(f"\n📊 ÚLTIMO MOVIMIENTO:")
            print(f"   Producto: {ultimo['producto']}")
            print(f"   Cantidad: {ultimo['cantidad']}")
            print(f"   Tipo: {ultimo['tipo']}")
            print(f"   Stock: {ultimo['stock_antes']} → {ultimo['stock_despues']}")
            print(f"   Fecha: {ultimo['fecha']}")
            
            if ultimo['cantidad'] > 0:
                print("\n   ✅ ES ENTRADA - CORRECTO")
            else:
                print("\n   ❌ ES SALIDA - VERIFICAR")
        else:
            print("No hay movimientos")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PRUEBAS DE STOCK")
    print("=" * 60)
    
    respuesta = input("\n¿Ejecutar prueba de AGREGAR stock (ENTRADA)? (s/n): ")
    if respuesta.lower() == 's':
        probar_agregar_stock()
        verificar_ultimo_movimiento()
    
    respuesta = input("\n¿Ejecutar prueba de QUITAR stock (SALIDA)? (s/n): ")
    if respuesta.lower() == 's':
        probar_quitar_stock()
        verificar_ultimo_movimiento()