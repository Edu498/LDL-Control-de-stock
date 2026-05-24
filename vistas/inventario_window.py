# -*- coding: utf-8 -*-
"""
Ventana de Ajuste Manual de Inventario (Entradas/Salidas/Mermas).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from controllers import StockController
from utils import Alertas

class AjusteStockWindow:
    """
    Diálogo modal para realizar ajustes manuales sobre el stock de un producto específico.

    Permite registrar incrementos (entradas) o decrementos (salidas/mermas) justificando
    el motivo del ajuste, actualizando la base de datos de manera inmediata.
    """

    def __init__(self, parent, producto, callback_refresh):
        """
        Inicializa e inicia el diálogo modal de ajuste de stock.

        Args:
            parent (tk.Widget): Ventana padre desde la cual se abre el diálogo.
            producto (Producto): Objeto `models.Producto` que se va a ajustar.
            callback_refresh (callable): Función a invocar tras guardar el ajuste para refrescar la lista de productos.
        """
        self.parent = parent
        self.producto = producto
        self.callback_refresh = callback_refresh
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Ajuste de Stock - {producto.nombre}")
        self.window.geometry("450x300")
        self.window.configure(bg='#F0F0F0')
        
        self.crear_widgets()
        
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()
    
    def crear_widgets(self):
        """
        Dibuja los controles del formulario de ajuste manual de stock.
        """
        # Título
        tk.Label(self.window, text=" AJUSTE DE STOCK", 
                font=("Arial", 14, "bold"), bg='#F0F0F0').pack(pady=10)
        
        # Frame principal
        frame = tk.Frame(self.window, bg='white', relief=tk.RAISED, bd=1)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Producto
        tk.Label(frame, text=f"Producto: {self.producto.nombre}", 
                bg='white', font=("Arial", 12)).pack(pady=10)
        
        tk.Label(frame, text=f"Código: {self.producto.codigo}", 
                bg='white').pack()
        
        tk.Label(frame, text=f"Stock Actual: {self.producto.stock_actual}", 
                bg='white', font=("Arial", 10, "bold")).pack(pady=10)
        
        # Tipo de ajuste
        tk.Label(frame, text="Tipo de ajuste:", bg='white').pack(pady=5)
        
        self.tipo_ajuste = tk.StringVar(value="entrada")
        tk.Radiobutton(frame, text="➕ Entrada (Agregar stock)", variable=self.tipo_ajuste,
                      value="entrada", bg='white').pack()
        tk.Radiobutton(frame, text="➖ Salida (Quitar stock)", variable=self.tipo_ajuste,
                      value="salida", bg='white').pack()
        
        # Cantidad
        tk.Label(frame, text="Cantidad:", bg='white').pack(pady=5)
        self.entry_cantidad = tk.Entry(frame, width=15, font=("Arial", 12))
        self.entry_cantidad.pack()
        
        # Motivo
        tk.Label(frame, text="Motivo:", bg='white').pack(pady=5)
        self.combo_motivo = ttk.Combobox(frame, values=[
            'Ajuste de inventario', 'Merma', 'Devolución', 'Corrección de stock'
        ], width=30)
        self.combo_motivo.pack()
        self.combo_motivo.set('Ajuste de inventario')
        
        # Botones
        frame_botones = tk.Frame(frame, bg='white')
        frame_botones.pack(pady=20)
        
        tk.Button(frame_botones, text=" Guardar", command=self.guardar_ajuste,
                 bg='#28A745', fg='white', padx=20).pack(side=tk.LEFT, padx=10)
        
        tk.Button(frame_botones, text="Cancelar", command=self.window.destroy,
                 bg='#6C757D', fg='white', padx=20).pack(side=tk.LEFT, padx=10)
    
    def guardar_ajuste(self):
        """
        Valida los datos ingresados y procesa la transacción de ajuste de stock en la base de datos.
        """
        try:
            cantidad = int(self.entry_cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except:
            Alertas.mostrar_mensaje_advertencia("Ingrese una cantidad válida")
            return
        
        if self.tipo_ajuste.get() == "salida":
            if cantidad > self.producto.stock_actual:
                Alertas.mostrar_mensaje_advertencia("No puede quitar más stock del que hay disponible")
                return
            cantidad = -cantidad
        
        tipo_movimiento = 3 if cantidad > 0 else 4  # 3=Ajuste positivo, 4=Ajuste negativo
        
        try:
            StockController.actualizar_stock(
                self.producto.id_producto,
                cantidad,
                tipo_movimiento,
                "admin",
                {'tipo': 'ajuste', 'motivo': self.combo_motivo.get()}
            )
            
            Alertas.mostrar_mensaje_exito("Stock actualizado correctamente")
            self.callback_refresh()
            self.window.destroy()
            
        except Exception as e:
            Alertas.mostrar_mensaje_error(f"Error al actualizar stock: {str(e)}")