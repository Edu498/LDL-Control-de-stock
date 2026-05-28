# diagnosticar.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.database import get_connection

"""
    Diagnosticar.py
    Módulo de diagnóstico de la base de datos
    En caso de error, mostrará los errores específicos de la base de datos
"""
def diagnosticar():
    """
    Diagnostica la base de datos y muestra información sobre los tipos de movimiento, 
    últimos 10 movimientos y productos con stock bajo
    """
    print("=" * 60)
    print("DIAGNÓSTICO DE BASE DE DATOS")
    print("=" * 60)
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Ver tipos de movimiento
        print("\n1. TIPOS DE MOVIMIENTO:")
        cursor.execute("SELECT * FROM tipos_movimiento")
        for t in cursor.fetchall():
            print(f"   ID: {t['id_tipo_movimiento']} | Nombre: {t['nombre']} | Signo: {t.get('signo', 'NO')}")
        
        # 2. Ver últimos 10 movimientos
        print("\n2. ÚLTIMOS 10 MOVIMIENTOS:")
        cursor.execute("""
            SELECT m.id_movimiento, m.cantidad, m.id_tipo_movimiento, 
                   m.stock_antes, m.stock_despues, p.nombre as producto,
                   DATE_FORMAT(m.fecha, '%d/%m/%Y %H:%i') as fecha
            FROM movimientos_stock m
            JOIN productos p ON m.id_producto = p.id_producto
            ORDER BY m.id_movimiento DESC
            LIMIT 10
        """)
        
        for m in cursor.fetchall():
            """
            Muestra los últimos 10 movimientos de la base de datos
            Args:
                m: Movimiento de la base de datos
            """
            tipo = "ENTRADA" if m['cantidad'] > 0 else "SALIDA"
            print(f"   ID:{m['id_movimiento']:3} | {m['producto'][:25]:25} | Cant:{m['cantidad']:4} | {tipo} | {m['fecha']}")
        
        # 3. Ver productos con stock bajo
        print("\n3. PRODUCTOS (primeros 5):")
        cursor.execute("SELECT id_producto, nombre, stock_actual, stock_minimo FROM productos LIMIT 5")
        for p in cursor.fetchall():
            """
            Muestra los productos con stock bajo de la base de datos
            Args:
                p: Producto de la base de datos
            """
            estado = "CRITICO" if p['stock_actual'] <= p['stock_minimo'] else "NORMAL"
            print(f"   ID:{p['id_producto']:2} | {p['nombre'][:25]:25} | Stock:{p['stock_actual']:3} | Min:{p['stock_minimo']} | {estado}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        """
        Maneja las excepciones que puedan ocurrir durante el diagnóstico
        Args:
            e: Excepción que ocurrió durante el diagnóstico
        """
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    """
    Función principal que ejecuta el diagnóstico de la base de datos
    """
    diagnosticar()