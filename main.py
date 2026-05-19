#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SISTEMA DE CONTROL DE STOCK
Versión 2.0.0
"""

import sys
import os

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print(" SISTEMA DE CONTROL DE STOCK v2.0.0")
print("=" * 60)
print("Iniciando aplicación...")
print("")

def main():
    """Función principal"""
    try:
        # Importar directamente desde vistas
        from vistas.login_window import LoginWindow
        app = LoginWindow()
    except ImportError as e:
        print(f"Error de importación: {e}")
        print("Verificando estructura alternativa...")
        
        try:
            # Método alternativo: ejecutar archivo directamente
            import os
            exec(open(os.path.join("vistas", "login_window.py")).read())
        except Exception as e2:
            print(f"Error alternativo: {e2}")
            input("Presione Enter para salir...")

if __name__ == "__main__":
    main()