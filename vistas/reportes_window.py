# -*- coding: utf-8 -*-
"""
Vistas de Reportes (Stock Actual, Movimientos y Ventas).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from controllers import ReporteController, StockController
from utils import formatear_precio, formatear_fecha

class ReporteStock:
    """
    Ventana para la visualización del reporte consolidado de stock actual.
    """
    
    def __init__(self, parent, id_producto=None):
        """
        Inicializa el reporte de stock.

        Args:
            parent (tk.Widget): Ventana padre.
            id_producto (int, opcional): ID del producto para filtrar (no utilizado actualmente).
        """
        self.parent = parent
        self.id_producto = id_producto
        
        self.window = tk.Toplevel(parent)
        self.window.title("Reporte de Stock")
        self.window.geometry("900x500")
        self.window.configure(bg='#F0F0F0')
        
        self.crear_widgets()
        self.cargar_datos()
        
        self.window.transient(parent)
        self.window.grab_set()
    
    def crear_widgets(self):
        """
        Dibuja la estructura de la ventana del reporte de stock.
        """
        tk.Label(self.window, text=" REPORTE DE STOCK ACTUAL", 
                font=("Arial", 16, "bold"), bg='#F0F0F0').pack(pady=10)
        
        frame_tabla = tk.Frame(self.window)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame_tabla)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas = ('Código', 'Producto', 'Categoría', 'Stock', 'Mínimo', 'Estado')
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings',
                                   yscrollcommand=scrollbar.set, height=20)
        
        for col in columnas:
            self.tabla.heading(col, text=col)
            ancho = 250 if col == 'Producto' else 120
            self.tabla.column(col, width=ancho)
        
        scrollbar.config(command=self.tabla.yview)
        self.tabla.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(self.window, text="Cerrar", command=self.window.destroy,
                 bg='#6C757D', fg='white', padx=20).pack(pady=10)
    
    def cargar_datos(self):
        """
        Consulta y llena la tabla con el catálogo y nivel de stock de cada producto.
        """
        productos = StockController.get_all_productos()
        
        for p in productos:
            estado, icono = p.estado_stock
            self.tabla.insert('', tk.END, values=(
                p.codigo, p.nombre, p.id_categoria or '-',
                p.stock_actual, p.stock_minimo, f"{icono} {estado}"
            ), tags=(estado,))
        
        self.tabla.tag_configure('NORMAL', background='#FFFFFF')
        self.tabla.tag_configure('STOCK BAJO', background='#FFF3CD')
        self.tabla.tag_configure('SIN STOCK', background='#F8D7DA')


class ReporteMovimientos:
    """
    Ventana para la visualización del historial detallado de movimientos de inventario.
    """
    
    def __init__(self, parent, id_producto=None):
        """
        Inicializa el reporte de movimientos.

        Args:
            parent (tk.Widget): Ventana padre.
            id_producto (int, opcional): ID de producto si se desea filtrar un artículo específico.
        """
        self.parent = parent
        self.id_producto = id_producto
        
        self.window = tk.Toplevel(parent)
        self.window.title("Reporte de Movimientos de Stock")
        self.window.geometry("1000x500")
        self.window.configure(bg='#F0F0F0')
        
        self.crear_widgets()
        self.cargar_datos()
        
        self.window.transient(parent)
        self.window.grab_set()
    
    def crear_widgets(self):
        """
        Dibuja los controles del listado de transacciones físicas de inventario.
        """
        tk.Label(self.window, text=" MOVIMIENTOS DE STOCK", 
                font=("Arial", 16, "bold"), bg='#F0F0F0').pack(pady=10)
        
        frame_tabla = tk.Frame(self.window)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar_y = tk.Scrollbar(frame_tabla)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = tk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columnas = ('Fecha', 'Producto', 'Tipo', 'Cantidad', 'Stock Antes', 'Stock Después', 'Usuario')
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings',
                                   yscrollcommand=scrollbar_y.set,
                                   xscrollcommand=scrollbar_x.set, height=20)
        
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=120)
        
        scrollbar_y.config(command=self.tabla.yview)
        scrollbar_x.config(command=self.tabla.xview)
        self.tabla.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(self.window, text="Cerrar", command=self.window.destroy,
                 bg='#6C757D', fg='white', padx=20).pack(pady=10)
    
    def cargar_datos(self):
        """
        Carga la bitácora de movimientos desde el controlador y la inserta en la tabla.
        """
        movimientos = ReporteController.get_movimientos_stock(self.id_producto, dias=90)
        
        for m in movimientos:
            signo = m['cantidad']
            color = '#28A745' if signo > 0 else '#DC3545'
            self.tabla.insert('', tk.END, values=(
                formatear_fecha(m['fecha']),
                m['producto'],
                m['tipo_movimiento'],
                signo,
                m['stock_antes'],
                m['stock_despues'],
                m.get('usuario', '-')
            ), tags=(color,))
        
        self.tabla.tag_configure('#28A745', foreground='#28A745')
        self.tabla.tag_configure('#DC3545', foreground='#DC3545')


class ReporteVentas:
    """
    Ventana para la visualización e impresión de reportes de facturación y ventas.
    """
    
    def __init__(self, parent):
        """
        Inicializa el reporte de ventas.

        Args:
            parent (tk.Widget): Ventana padre.
        """
        self.parent = parent
        
        self.window = tk.Toplevel(parent)
        self.window.title("Reporte de Ventas")
        self.window.geometry("1000x600")
        self.window.configure(bg='#F0F0F0')
        
        self.crear_widgets()
        self.cargar_datos()
        
        self.window.transient(parent)
        self.window.grab_set()
    
    def crear_widgets(self):
        """
        Dibuja los filtros de búsqueda temporal, la tabla de ventas y el ranking de artículos más vendidos.
        """
        tk.Label(self.window, text=" REPORTE DE VENTAS", 
                font=("Arial", 16, "bold"), bg='#F0F0F0').pack(pady=10)
        
        # Frame de filtros
        frame_filtros = tk.Frame(self.window, bg='white', relief=tk.RAISED, bd=1)
        frame_filtros.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(frame_filtros, text="Período:", bg='white').pack(side=tk.LEFT, padx=10, pady=10)
        
        self.combo_periodo = ttk.Combobox(frame_filtros, values=['Hoy', 'Última Semana', 'Último Mes', 'Personalizado'], width=20)
        self.combo_periodo.pack(side=tk.LEFT, padx=5)
        self.combo_periodo.set('Hoy')
        self.combo_periodo.bind('<<ComboboxSelected>>', self.cambiar_periodo)
        
        tk.Label(frame_filtros, text="Desde:", bg='white').pack(side=tk.LEFT, padx=10)
        self.entry_desde = tk.Entry(frame_filtros, width=12)
        self.entry_desde.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_filtros, text="Hasta:", bg='white').pack(side=tk.LEFT, padx=10)
        self.entry_hasta = tk.Entry(frame_filtros, width=12)
        self.entry_hasta.pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_filtros, text=" Mostrar", command=self.cargar_datos,
                 bg='#007BFF', fg='white').pack(side=tk.LEFT, padx=20)
        
        # Tabla de ventas
        frame_tabla = tk.Frame(self.window)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame_tabla)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas = ('Fecha', 'Factura', 'Cliente', 'Total')
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings',
                                   yscrollcommand=scrollbar.set, height=20)
        
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=200 if col == 'Cliente' else 150)
        
        scrollbar.config(command=self.tabla.yview)
        self.tabla.pack(fill=tk.BOTH, expand=True)
        
        # Tabla de productos más vendidos
        tk.Label(self.window, text=" PRODUCTOS MÁS VENDIDOS", 
                font=("Arial", 14, "bold"), bg='#F0F0F0').pack(pady=10)
        
        frame_top = tk.Frame(self.window)
        frame_top.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar_top = tk.Scrollbar(frame_top)
        scrollbar_top.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas_top = ('Producto', 'Cantidad Vendida', 'N° Ventas', 'Ingreso Total')
        self.tabla_top = ttk.Treeview(frame_top, columns=columnas_top, show='headings',
                                       yscrollcommand=scrollbar_top.set, height=8)
        
        for col in columnas_top:
            self.tabla_top.heading(col, text=col)
            self.tabla_top.column(col, width=200 if col == 'Producto' else 150)
        
        scrollbar_top.config(command=self.tabla_top.yview)
        self.tabla_top.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(self.window, text="Cerrar", command=self.window.destroy,
                 bg='#6C757D', fg='white', padx=20).pack(pady=10)
        
        self.cambiar_periodo()
    
    def cambiar_periodo(self, event=None):
        """
        Actualiza los campos de fecha de inicio y fin según el período seleccionado.
        """
        periodo = self.combo_periodo.get()
        
        if periodo == 'Hoy':
            self.entry_desde.delete(0, tk.END)
            self.entry_hasta.delete(0, tk.END)
            self.entry_desde.insert(0, datetime.now().strftime('%d/%m/%Y'))
            self.entry_hasta.insert(0, datetime.now().strftime('%d/%m/%Y'))
            self.entry_desde.config(state='readonly')
            self.entry_hasta.config(state='readonly')
        elif periodo == 'Última Semana':
            self.entry_desde.config(state='normal')
            self.entry_hasta.config(state='normal')
            desde = datetime.now() - timedelta(days=7)
            self.entry_desde.delete(0, tk.END)
            self.entry_hasta.delete(0, tk.END)
            self.entry_desde.insert(0, desde.strftime('%d/%m/%Y'))
            self.entry_hasta.insert(0, datetime.now().strftime('%d/%m/%Y'))
            self.entry_desde.config(state='readonly')
            self.entry_hasta.config(state='readonly')
        elif periodo == 'Último Mes':
            self.entry_desde.config(state='normal')
            self.entry_hasta.config(state='normal')
            desde = datetime.now() - timedelta(days=30)
            self.entry_desde.delete(0, tk.END)
            self.entry_hasta.delete(0, tk.END)
            self.entry_desde.insert(0, desde.strftime('%d/%m/%Y'))
            self.entry_hasta.insert(0, datetime.now().strftime('%d/%m/%Y'))
            self.entry_desde.config(state='readonly')
            self.entry_hasta.config(state='readonly')
        else:
            self.entry_desde.config(state='normal')
            self.entry_hasta.config(state='normal')
            self.entry_desde.delete(0, tk.END)
            self.entry_hasta.delete(0, tk.END)
    
    def cargar_datos(self):
        """
        Carga los productos más vendidos desde la base de datos y refresca las tablas.
        """
        # Cargar productos más vendidos
        productos_top = ReporteController.get_productos_mas_vendidos(10)
        
        for item in self.tabla_top.get_children():
            self.tabla_top.delete(item)
        
        for p in productos_top:
            self.tabla_top.insert('', tk.END, values=(
                p['nombre'],
                p['total_vendido'],
                p['numero_ventas'],
                formatear_precio(p['ingreso_total'])
            ))
        
        Alertas.mostrar_mensaje_informacion("Reporte", "Reporte cargado correctamente")


from utils.alertas import Alertas