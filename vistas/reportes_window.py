# vistas/reportes_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from controllers.reporte_controller import ReporteController
from controllers.stock_controller import StockController
from utils.helpers import formatear_precio, formatear_fecha
from utils.alertas import Alertas
from utils.database import get_connection
import csv

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False


class ReporteStock:
    """Reporte de stock actual"""
    
    def __init__(self, parent, id_producto=None):
        self.parent = parent
        self.id_producto = id_producto
        self.tabla = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Reporte de Stock")
        self.window.geometry("900x500")
        self.window.configure(bg='#F0F0F0')
        
        self.crear_widgets()
        self.cargar_datos()
        
        self.window.transient(parent)
        self.window.grab_set()
    
    def crear_widgets(self):
        tk.Label(self.window, text="REPORTE DE STOCK ACTUAL", 
                font=("Arial", 16, "bold"), bg='#F0F0F0').pack(pady=10)
        
        frame_tabla = tk.Frame(self.window)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame_tabla)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas = ('Codigo', 'Producto', 'Categoria', 'Stock', 'Minimo', 'Estado')
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
        if not self.tabla:
            return
        
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        productos = StockController.get_all_productos()
        
        for p in productos:
            estado = p.estado_stock
            icono = p.icono_estado
            
            self.tabla.insert('', tk.END, values=(
                p.codigo, p.nombre, p.id_categoria or '-',
                p.stock_actual, p.stock_minimo, f"{icono} {estado}"
            ), tags=(estado,))
        
        self.tabla.tag_configure('NORMAL', background='#FFFFFF')
        self.tabla.tag_configure('STOCK BAJO', background='#FFF3CD')
        self.tabla.tag_configure('SIN STOCK', background='#F8D7DA')


class ReporteMovimientos:
    """Reporte de movimientos de stock - ENTRADAS (cantidad > 0) y SALIDAS (cantidad < 0)"""
    
    def __init__(self, parent, id_producto=None):
        self.parent = parent
        self.id_producto = id_producto
        self.producto_nombre = None
        self.movimientos = []
        self.movimientos_filtrados = []
        
        self.window = tk.Toplevel(parent)
        self.window.title("Reporte de Movimientos de Stock")
        self.window.geometry("1300x650")
        self.window.configure(bg='#F0F0F0')
        
        if id_producto:
            producto = StockController.get_producto_by_id(id_producto)
            if producto:
                self.producto_nombre = producto.nombre
                self.window.title(f"Movimientos de Stock - {self.producto_nombre}")
        
        self.crear_widgets()
        self.cargar_movimientos()
        
        self.window.transient(parent)
        self.window.grab_set()
    
    def crear_widgets(self):
        # Encabezado
        titulo = "MOVIMIENTOS DE STOCK"
        if self.producto_nombre:
            titulo = f"MOVIMIENTOS DE STOCK - {self.producto_nombre}"
        
        tk.Label(self.window, text=titulo, 
                font=("Arial", 16, "bold"), bg='#F0F0F0', fg='#2C3E50').pack(pady=10)
        
        # FRAME DE FILTROS
        filtros_frame = tk.Frame(self.window, bg='white', relief=tk.RAISED, bd=1)
        filtros_frame.pack(fill=tk.X, padx=10, pady=10)
        
        filtros_inner = tk.Frame(filtros_frame, bg='white')
        filtros_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Fecha desde
        tk.Label(filtros_inner, text="Desde:", bg='white', font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_desde = tk.Entry(filtros_inner, width=12, font=("Arial", 10), bg='white')
        self.entry_desde.grid(row=0, column=1, padx=5, pady=5)
        self.entry_desde.insert(0, (datetime.now() - timedelta(days=30)).strftime('%d/%m/%Y'))
        
        # Fecha hasta
        tk.Label(filtros_inner, text="Hasta:", bg='white', font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.entry_hasta = tk.Entry(filtros_inner, width=12, font=("Arial", 10), bg='white')
        self.entry_hasta.grid(row=0, column=3, padx=5, pady=5)
        self.entry_hasta.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        # Tipo
        tk.Label(filtros_inner, text="Tipo:", bg='white', font=("Arial", 10, "bold")).grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.combo_tipo = ttk.Combobox(filtros_inner, values=['TODOS', 'ENTRADA', 'SALIDA'], width=12)
        self.combo_tipo.grid(row=0, column=5, padx=5, pady=5)
        self.combo_tipo.set('TODOS')
        
        # Botones
        tk.Button(filtros_inner, text="Filtrar", command=self.filtrar_movimientos,
                 bg='#007BFF', fg='white', font=("Arial", 10, "bold"),
                 padx=15, pady=5, cursor='hand2').grid(row=0, column=6, padx=10, pady=5)
        
        tk.Button(filtros_inner, text="Actualizar", command=self.cargar_movimientos,
                 bg='#28A745', fg='white', font=("Arial", 10, "bold"),
                 padx=15, pady=5, cursor='hand2').grid(row=0, column=7, padx=5, pady=5)
        
        tk.Button(filtros_inner, text="Exportar CSV", command=self.exportar_csv,
                 bg='#17A2B8', fg='white', font=("Arial", 10, "bold"),
                 padx=15, pady=5, cursor='hand2').grid(row=0, column=8, padx=5, pady=5)
        
        # TARJETAS DE RESUMEN
        resumen_frame = tk.Frame(self.window, bg='#F0F0F0')
        resumen_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Entradas
        card1 = tk.Frame(resumen_frame, bg='white', relief=tk.RAISED, bd=1)
        card1.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        tk.Label(card1, text="ENTRADAS", font=("Arial", 11, "bold"),
                bg='white', fg='#28A745').pack(pady=(10, 5))
        self.lbl_entradas = tk.Label(card1, text="0", font=("Arial", 24, "bold"),
                                     bg='white', fg='#28A745')
        self.lbl_entradas.pack()
        self.lbl_num_entradas = tk.Label(card1, text="0 movimientos", font=("Arial", 9),
                                         bg='white', fg='#6C757D')
        self.lbl_num_entradas.pack(pady=(0, 10))
        
        # Salidas
        card2 = tk.Frame(resumen_frame, bg='white', relief=tk.RAISED, bd=1)
        card2.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        tk.Label(card2, text="SALIDAS", font=("Arial", 11, "bold"),
                bg='white', fg='#DC3545').pack(pady=(10, 5))
        self.lbl_salidas = tk.Label(card2, text="0", font=("Arial", 24, "bold"),
                                    bg='white', fg='#DC3545')
        self.lbl_salidas.pack()
        self.lbl_num_salidas = tk.Label(card2, text="0 movimientos", font=("Arial", 9),
                                        bg='white', fg='#6C757D')
        self.lbl_num_salidas.pack(pady=(0, 10))
        
        # Balance
        card3 = tk.Frame(resumen_frame, bg='white', relief=tk.RAISED, bd=1)
        card3.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        tk.Label(card3, text="BALANCE", font=("Arial", 11, "bold"),
                bg='white', fg='#FFC107').pack(pady=(10, 5))
        self.lbl_balance = tk.Label(card3, text="0", font=("Arial", 24, "bold"),
                                    bg='white', fg='#FFC107')
        self.lbl_balance.pack()
        self.lbl_periodo = tk.Label(card3, text="Ultimos 30 dias", font=("Arial", 9),
                                    bg='white', fg='#6C757D')
        self.lbl_periodo.pack(pady=(0, 10))
        
        # Total movimientos
        card4 = tk.Frame(resumen_frame, bg='white', relief=tk.RAISED, bd=1)
        card4.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        tk.Label(card4, text="TOTAL", font=("Arial", 11, "bold"),
                bg='white', fg='#17A2B8').pack(pady=(10, 5))
        self.lbl_total = tk.Label(card4, text="0", font=("Arial", 24, "bold"),
                                  bg='white', fg='#17A2B8')
        self.lbl_total.pack()
        self.lbl_total_mov = tk.Label(card4, text="movimientos", font=("Arial", 9),
                                      bg='white', fg='#6C757D')
        self.lbl_total_mov.pack(pady=(0, 10))
        
        # TABLA DE MOVIMIENTOS
        frame_tabla = tk.Frame(self.window)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scroll_y = tk.Scrollbar(frame_tabla)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = tk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columnas = ('Fecha', 'Hora', 'Producto', 'Codigo', 'Tipo', 'Cantidad', 
                   'Stock Antes', 'Stock Despues', 'Usuario', 'Motivo')
        
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings',
                                   yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                                   height=20)
        
        anchos = {'Fecha': 90, 'Hora': 70, 'Producto': 200, 'Codigo': 90,
                  'Tipo': 70, 'Cantidad': 70, 'Stock Antes': 90, 
                  'Stock Despues': 90, 'Usuario': 90, 'Motivo': 150}
        
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=anchos.get(col, 100))
        
        scroll_y.config(command=self.tabla.yview)
        scroll_x.config(command=self.tabla.xview)
        self.tabla.pack(fill=tk.BOTH, expand=True)
        
        # Configurar colores: ENTRADA fondo verde claro, SALIDA fondo rojo claro
        self.tabla.tag_configure('ENTRADA', background='#D4EDDA')
        self.tabla.tag_configure('SALIDA', background='#F8D7DA')
        
        # BOTONES INFERIORES
        btn_frame = tk.Frame(self.window, bg='#F0F0F0')
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(btn_frame, text="Refrescar", command=self.refrescar_datos,
                 bg='#28A745', fg='white', font=("Arial", 10, "bold"),
                 padx=20, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Ver Detalle", command=self.ver_detalle,
                 bg='#17A2B8', fg='white', font=("Arial", 10, "bold"),
                 padx=20, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Resumen por Producto", command=self.resumen_por_producto,
                 bg='#6C757D', fg='white', font=("Arial", 10, "bold"),
                 padx=20, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Cerrar", command=self.window.destroy,
                 bg='#DC3545', fg='white', font=("Arial", 10, "bold"),
                 padx=20, pady=8, cursor='hand2').pack(side=tk.RIGHT, padx=5)
        
        # Footer
        footer = tk.Label(self.window, text="Doble clic para ver detalle | Cantidad > 0 = ENTRADA | Cantidad < 0 = SALIDA",
                         font=("Arial", 8), bg='#F0F0F0', fg='#6C757D')
        footer.pack(pady=5)
        
        self.tabla.bind('<Double-Button-1>', self.ver_detalle_event)
    
    def refrescar_datos(self):
        """Recarga los datos desde la base de datos"""
        print("Refrescando datos...")
        self.cargar_movimientos()
        messagebox.showinfo("Actualizado", "Los datos han sido actualizados")
    
    def cargar_movimientos(self):
        """Carga los movimientos desde la base de datos"""
        try:
            self.movimientos = ReporteController.get_movimientos_stock(self.id_producto, dias=365)
            print(f"DEBUG: Se encontraron {len(self.movimientos)} movimientos")
            self.filtrar_movimientos()
        except Exception as e:
            print(f"Error: {e}")
            self.movimientos = []
            self.movimientos_filtrados = []
    
    def filtrar_movimientos(self):
        """Filtra por fecha y tipo"""
        try:
            desde = datetime.strptime(self.entry_desde.get(), '%d/%m/%Y')
            hasta = datetime.strptime(self.entry_hasta.get(), '%d/%m/%Y')
            hasta = hasta.replace(hour=23, minute=59, second=59)
        except:
            desde = datetime.now() - timedelta(days=30)
            hasta = datetime.now()
        
        tipo_filtro = self.combo_tipo.get()
        
        filtrados = []
        for m in self.movimientos:
            fecha_mov = m['fecha'] if isinstance(m['fecha'], datetime) else datetime.strptime(str(m['fecha']), '%Y-%m-%d %H:%M:%S')
            
            if fecha_mov < desde or fecha_mov > hasta:
                continue
            
            if tipo_filtro != 'TODOS':
                # ENTRADA si cantidad > 0, SALIDA si cantidad < 0
                tipo_mov = 'ENTRADA' if m['cantidad'] > 0 else 'SALIDA'
                if tipo_mov != tipo_filtro:
                    continue
            
            filtrados.append(m)
        
        self.movimientos_filtrados = filtrados
        self.actualizar_tabla()
        self.actualizar_resumen()
        self.lbl_periodo.config(text=f"{self.entry_desde.get()} - {self.entry_hasta.get()}")
    
    def actualizar_tabla(self):
        """Actualiza la tabla con los movimientos"""
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        if not self.movimientos_filtrados:
            self.tabla.insert('', tk.END, values=('No hay movimientos', '', '', '', '', '', '', '', '', ''))
            return
        
        for m in self.movimientos_filtrados:
            # ENTRADA si cantidad > 0, SALIDA si cantidad < 0
            if m['cantidad'] > 0:
                tipo = 'ENTRADA'
                cantidad = m['cantidad']
            else:
                tipo = 'SALIDA'
                cantidad = abs(m['cantidad'])
            
            fecha_obj = m['fecha'] if isinstance(m['fecha'], datetime) else datetime.strptime(str(m['fecha']), '%Y-%m-%d %H:%M:%S')
            
            self.tabla.insert('', tk.END, values=(
                fecha_obj.strftime('%d/%m/%Y'),
                fecha_obj.strftime('%H:%M:%S'),
                m.get('producto_nombre', 'N/A'),
                m.get('producto_codigo', 'N/A'),
                tipo,
                cantidad,
                m['stock_antes'],
                m['stock_despues'],
                m.get('usuario', 'admin'),
                m.get('referencia_tipo', 'Ajuste')
            ), tags=(tipo,))
    
    def actualizar_resumen(self):
        """Actualiza tarjetas de resumen"""
        total_entradas = 0
        total_salidas = 0
        num_entradas = 0
        num_salidas = 0
        
        for m in self.movimientos_filtrados:
            if m['cantidad'] > 0:
                total_entradas += m['cantidad']
                num_entradas += 1
            else:
                total_salidas += abs(m['cantidad'])
                num_salidas += 1
        
        balance = total_entradas - total_salidas
        
        self.lbl_entradas.config(text=f"{total_entradas}")
        self.lbl_num_entradas.config(text=f"{num_entradas} movimientos")
        
        self.lbl_salidas.config(text=f"{total_salidas}")
        self.lbl_num_salidas.config(text=f"{num_salidas} movimientos")
        
        balance_color = '#28A745' if balance >= 0 else '#DC3545'
        self.lbl_balance.config(text=f"{balance}", fg=balance_color)
        
        total = len(self.movimientos_filtrados)
        self.lbl_total.config(text=f"{total}")
        self.lbl_total_mov.config(text="movimientos")
    
    def ver_detalle(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Información", "Seleccione un movimiento")
            return
        self.mostrar_detalle()
    
    def ver_detalle_event(self, event):
        self.mostrar_detalle()
    
    def mostrar_detalle(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        
        item = self.tabla.item(seleccion[0])
        valores = item['values']
        
        detalle = tk.Toplevel(self.window)
        detalle.title("Detalle del Movimiento")
        detalle.geometry("450x400")
        detalle.configure(bg='#F0F0F0')
        detalle.resizable(False, False)
        detalle.transient(self.window)
        detalle.grab_set()
        
        frame = tk.Frame(detalle, bg='white', relief=tk.RAISED, bd=1, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="DETALLE DEL MOVIMIENTO", font=("Arial", 14, "bold"),
                bg='white', fg='#2C3E50').pack(pady=10)
        
        datos = [
            ("Fecha:", valores[0]),
            ("Hora:", valores[1]),
            ("Producto:", valores[2]),
            ("Código:", valores[3]),
            ("Tipo:", valores[4]),
            ("Cantidad:", valores[5]),
            ("Stock Anterior:", valores[6]),
            ("Stock Nuevo:", valores[7]),
            ("Usuario:", valores[8]),
            ("Motivo:", valores[9])
        ]
        
        for label, valor in datos:
            row = tk.Frame(frame, bg='white')
            row.pack(fill=tk.X, pady=5)
            tk.Label(row, text=label, font=("Arial", 10, "bold"),
                    bg='white', fg='#495057', width=15, anchor='w').pack(side=tk.LEFT)
            tk.Label(row, text=str(valor), font=("Arial", 10),
                    bg='white', fg='#2C3E50', anchor='w').pack(side=tk.LEFT, padx=10)
        
        tk.Button(frame, text="Cerrar", command=detalle.destroy,
                 bg='#6C757D', fg='white', font=("Arial", 10, "bold"),
                 padx=20, pady=8, cursor='hand2').pack(pady=20)
    
    def resumen_por_producto(self):
        if not self.movimientos_filtrados:
            messagebox.showinfo("Información", "No hay datos para mostrar")
            return
        
        resumen = {}
        for m in self.movimientos_filtrados:
            nombre = m.get('producto_nombre', 'Desconocido')
            if nombre not in resumen:
                resumen[nombre] = {'entradas': 0, 'salidas': 0}
            
            if m['cantidad'] > 0:
                resumen[nombre]['entradas'] += m['cantidad']
            else:
                resumen[nombre]['salidas'] += abs(m['cantidad'])
        
        win = tk.Toplevel(self.window)
        win.title("Resumen por Producto")
        win.geometry("600x400")
        win.configure(bg='#F0F0F0')
        
        frame = tk.Frame(win, bg='white', relief=tk.RAISED, bd=1, padx=15, pady=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="RESUMEN POR PRODUCTO", font=("Arial", 14, "bold"),
                bg='white', fg='#2C3E50').pack(pady=10)
        
        tabla_frame = tk.Frame(frame)
        tabla_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll = tk.Scrollbar(tabla_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas = ('Producto', 'Entradas', 'Salidas', 'Balance')
        tabla = ttk.Treeview(tabla_frame, columns=columnas, show='headings',
                              yscrollcommand=scroll.set, height=15)
        
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=200 if col == 'Producto' else 100)
        
        scroll.config(command=tabla.yview)
        tabla.pack(fill=tk.BOTH, expand=True)
        
        for nombre, datos in sorted(resumen.items()):
            balance = datos['entradas'] - datos['salidas']
            tabla.insert('', tk.END, values=(nombre, datos['entradas'], datos['salidas'], balance))
        
        tk.Button(frame, text="Cerrar", command=win.destroy,
                 bg='#6C757D', fg='white', padx=20, pady=5).pack(pady=10)
    
    def exportar_csv(self):
        if not self.movimientos_filtrados:
            messagebox.showwarning("Advertencia", "No hay datos para exportar")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"movimientos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Fecha', 'Hora', 'Producto', 'Código', 'Tipo', 'Cantidad', 
                                'Stock Antes', 'Stock Despues', 'Usuario', 'Motivo'])
                
                for m in self.movimientos_filtrados:
                    tipo = 'ENTRADA' if m['cantidad'] > 0 else 'SALIDA'
                    fecha_obj = m['fecha'] if isinstance(m['fecha'], datetime) else datetime.strptime(str(m['fecha']), '%Y-%m-%d %H:%M:%S')
                    
                    writer.writerow([
                        fecha_obj.strftime('%d/%m/%Y'),
                        fecha_obj.strftime('%H:%M:%S'),
                        m.get('producto_nombre', 'N/A'),
                        m.get('producto_codigo', 'N/A'),
                        tipo,
                        abs(m['cantidad']),
                        m['stock_antes'],
                        m['stock_despues'],
                        m.get('usuario', 'admin'),
                        m.get('referencia_tipo', 'Ajuste')
                    ])
            
            messagebox.showinfo("Éxito", f"Archivo exportado:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {e}")


class ReporteVentas:
    """Reporte de ventas - Filtro por periodo funcional"""
    
    def __init__(self, parent):
        self.parent = parent
        self.tabla = None
        self.tabla_top = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Reporte de Ventas")
        self.window.geometry("1000x600")
        self.window.configure(bg='#F0F0F0')
        
        self.crear_widgets()
        
        self.window.transient(parent)
        self.window.grab_set()
    
    def crear_widgets(self):
        tk.Label(self.window, text="REPORTE DE VENTAS", 
                font=("Arial", 16, "bold"), bg='#F0F0F0').pack(pady=10)
        
        # Filtros
        frame_filtros = tk.Frame(self.window, bg='white', relief=tk.RAISED, bd=1)
        frame_filtros.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(frame_filtros, text="Periodo:", bg='white', font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=10, pady=10)
        
        self.combo_periodo = ttk.Combobox(frame_filtros, values=['Hoy', 'Ultima Semana', 'Ultimo Mes', 'Ultimo Año', 'Todos'], width=20)
        self.combo_periodo.pack(side=tk.LEFT, padx=5)
        self.combo_periodo.set('Ultima Semana')
        self.combo_periodo.bind('<<ComboboxSelected>>', lambda e: self.cargar_ventas())
        
        tk.Button(frame_filtros, text="Mostrar", command=self.cargar_ventas,
                 bg='#007BFF', fg='white', font=("Arial", 10, "bold"),
                 padx=15, pady=5, cursor='hand2').pack(side=tk.LEFT, padx=20)
        
        # Tabla de ventas
        frame_tabla = tk.Frame(self.window)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame_tabla)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas = ('Fecha', 'Factura', 'Cliente', 'Total')
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings',
                                   yscrollcommand=scrollbar.set, height=15)
        
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=200 if col == 'Cliente' else 150)
        
        scrollbar.config(command=self.tabla.yview)
        self.tabla.pack(fill=tk.BOTH, expand=True)
        
        # Productos más vendidos
        tk.Label(self.window, text="PRODUCTOS MAS VENDIDOS", 
                font=("Arial", 14, "bold"), bg='#F0F0F0').pack(pady=10)
        
        frame_top = tk.Frame(self.window)
        frame_top.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar_top = tk.Scrollbar(frame_top)
        scrollbar_top.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas_top = ('Producto', 'Cantidad Vendida', 'N Ventas', 'Ingreso Total')
        self.tabla_top = ttk.Treeview(frame_top, columns=columnas_top, show='headings',
                                       yscrollcommand=scrollbar_top.set, height=8)
        
        for col in columnas_top:
            self.tabla_top.heading(col, text=col)
            self.tabla_top.column(col, width=200 if col == 'Producto' else 150)
        
        scrollbar_top.config(command=self.tabla_top.yview)
        self.tabla_top.pack(fill=tk.BOTH, expand=True)
        
        # Botón cerrar
        tk.Button(self.window, text="Cerrar", command=self.window.destroy,
                 bg='#DC3545', fg='white', font=("Arial", 10, "bold"),
                 padx=20, pady=8, cursor='hand2').pack(pady=10)
        
        # Cargar datos iniciales
        self.cargar_productos_mas_vendidos()
        self.cargar_ventas()
    
    def cargar_ventas(self):
        """Carga las ventas según el periodo seleccionado"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        periodo = self.combo_periodo.get()
        
        # Calcular fechas según periodo
        hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if periodo == 'Hoy':
            fecha_inicio = hoy
            fecha_fin = hoy.replace(hour=23, minute=59, second=59)
        elif periodo == 'Ultima Semana':
            fecha_inicio = hoy - timedelta(days=7)
            fecha_fin = hoy.replace(hour=23, minute=59, second=59)
        elif periodo == 'Ultimo Mes':
            fecha_inicio = hoy - timedelta(days=30)
            fecha_fin = hoy.replace(hour=23, minute=59, second=59)
        elif periodo == 'Ultimo Año':
            fecha_inicio = hoy - timedelta(days=365)
            fecha_fin = hoy.replace(hour=23, minute=59, second=59)
        else:  # Todos
            fecha_inicio = datetime(2020, 1, 1)
            fecha_fin = hoy.replace(hour=23, minute=59, second=59)
        
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    DATE_FORMAT(fecha_venta, '%d/%m/%Y') as fecha,
                    numero_factura,
                    cliente_nombre,
                    total
                FROM ventas
                WHERE fecha_venta BETWEEN %s AND %s
                AND id_estado = 2
                ORDER BY fecha_venta DESC
            """, (fecha_inicio, fecha_fin))
            
            ventas = cursor.fetchall()
            
            if not ventas:
                self.tabla.insert('', tk.END, values=('No hay ventas en este periodo', '', '', ''))
            else:
                total_general = 0
                for v in ventas:
                    self.tabla.insert('', tk.END, values=(
                        v['fecha'],
                        v['numero_factura'] or 'S/N',
                        v['cliente_nombre'] or 'CONSUMIDOR FINAL',
                        f"${v['total']:,.2f}"
                    ))
                    total_general += v['total']
                
                # Agregar fila de total
                self.tabla.insert('', tk.END, values=('', '', 'TOTAL:', f"${total_general:,.2f}"))
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error cargando ventas: {e}")
            self.tabla.insert('', tk.END, values=(f'Error: {str(e)}', '', '', ''))
    
    def cargar_productos_mas_vendidos(self):
        """Carga los productos más vendidos (todos los tiempos)"""
        for item in self.tabla_top.get_children():
            self.tabla_top.delete(item)
        
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    p.nombre,
                    COALESCE(SUM(dv.cantidad), 0) AS total_vendido,
                    COUNT(DISTINCT dv.id_venta) AS numero_ventas,
                    COALESCE(SUM(dv.subtotal), 0) AS ingreso_total
                FROM productos p
                LEFT JOIN detalles_venta dv ON p.id_producto = dv.id_producto
                LEFT JOIN ventas v ON dv.id_venta = v.id_venta AND v.id_estado = 2
                WHERE p.activo = TRUE
                GROUP BY p.id_producto, p.nombre
                HAVING total_vendido > 0
                ORDER BY total_vendido DESC
                LIMIT 10
            """)
            
            productos_top = cursor.fetchall()
            
            if not productos_top:
                self.tabla_top.insert('', tk.END, values=('No hay ventas', '0', '0', '$0.00'))
            else:
                for p in productos_top:
                    self.tabla_top.insert('', tk.END, values=(
                        p['nombre'],
                        p['total_vendido'],
                        p['numero_ventas'],
                        f"${p['ingreso_total']:,.2f}"
                    ))
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error cargando productos más vendidos: {e}")
            self.tabla_top.insert('', tk.END, values=(f'Error: {str(e)}', '0', '0', '$0.00'))