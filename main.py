# main.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import codecs

# Configurar codificacion
if sys.stdout.encoding != 'UTF-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print(" SISTEMA DE CONTROL DE STOCK v2.0.0")
print("=" * 60)
print("Iniciando aplicacion...")
print("")

def main():
    try:
        from vistas.login_window import LoginWindow
        app = LoginWindow()
    except ImportError as e:
        print(f"Error de importacion: {e}")
        try:
            with open(os.path.join("vistas", "login_window.py"), 'r', encoding='utf-8') as f:
                exec(f.read())
        except Exception as e2:
            print(f"Error alternativo: {e2}")
            input("Presione Enter para salir...")

if __name__ == "__main__":
    main()