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

import atexit
import subprocess

def iniciar_api():
    try:
        print("Iniciando API de integracion (segundo plano)...")
        # Evitar que se abra una ventana extra de consola en Windows
        flags = 0x08000000 if os.name == 'nt' else 0
            
        api_proceso = subprocess.Popen([sys.executable, "api_ventas.py"], 
                                   creationflags=flags,
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
        
        def matar_proceso():
            print("Cerrando API de integracion...")
            api_proceso.terminate()
            
        atexit.register(matar_proceso)
    except Exception as e:
        print(f"No se pudo iniciar la API: {e}")

def main():
    iniciar_api()
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