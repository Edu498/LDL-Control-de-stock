# -*- coding: utf-8 -*-
"""
Script de verificación de la estructura de directorios del proyecto.

Este script comprueba la existencia de los directorios clave del proyecto
(`models`, `controllers`, `vistas`, `utils`) así como los archivos
principales de ejecución (`main.py` y `config.py`).
"""
import os
import sys

def verificar():
    print("="*50)
    print("VERIFICANDO ESTRUCTURA DEL PROYECTO")
    print("="*50)

    carpeta_actual = os.getcwd()
    print(f"\n📁 Carpeta actual: {carpeta_actual}")

    # Verificar carpetas necesarias
    carpetas = ['models', 'controllers', 'vistas', 'utils']
    for carpeta in carpetas:
        ruta = os.path.join(carpeta_actual, carpeta)
        if os.path.exists(ruta):
            print(f"✅ Carpeta '{carpeta}' existe")
            # Verificar archivos dentro
            archivos = os.listdir(ruta)
            print(f"   Archivos: {', '.join(archivos[:5])}")
        else:
            print(f"❌ Carpeta '{carpeta}' NO existe")

    # Verificar archivo main.py
    if os.path.exists(os.path.join(carpeta_actual, 'main.py')):
        print("✅ main.py existe")
    else:
        print("❌ main.py NO existe")

    # Verificar config.py
    if os.path.exists(os.path.join(carpeta_actual, 'config.py')):
        print("✅ config.py existe")
    else:
        print("❌ config.py NO existe")

    print("\n" + "="*50)
    print("Para ejecutar el sistema, usa:")
    print("cd C:/Users/Jorge/control_stock")
    print("python main.py")
    print("="*50)

if __name__ == "__main__":
    verificar()
