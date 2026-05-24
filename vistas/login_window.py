# -*- coding: utf-8 -*-
"""
Ventana de Login y Autenticación del Sistema.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

class LoginWindow:
    """
    Representa la ventana de inicio de sesión de la aplicación.

    Crea una interfaz Tkinter donde el usuario ingresa sus credenciales de acceso.
    Si las credenciales son válidas, abre la ventana principal (`MainWindow`) y destruye la ventana de login.
    """
    
    def __init__(self):
        """
        Inicializa y configura la ventana de login, cargando la interfaz y los manejadores de eventos.
        """
        self.window = tk.Tk()
        self.window.title("Sistema de Control de Stock - Login")
        self.window.geometry("450x420")
        self.window.configure(bg='#F0F4F8')
        self.window.resizable(False, False)
        
        # Centrar ventana
        self.window.eval('tk::PlaceWindow . center')
        
        self._crear_interfaz()
        self._configurar_eventos()
        
        self.window.mainloop()
    
    def _crear_interfaz(self):
        """
        Crea los controles y el diseño visual de la ventana de login.
        """
        frame = tk.Frame(self.window, bg='white', relief=tk.RAISED, bd=1)
        frame.pack(expand=True, fill=tk.BOTH, padx=25, pady=25)
        
        tk.Label(frame, text="📦", font=("Segoe UI", 48), bg='white').pack(pady=(20, 5))
        tk.Label(frame, text="CONTROL DE STOCK", font=("Segoe UI", 18, "bold"), bg='white', fg='#2C3E50').pack()
        tk.Label(frame, text="Sistema de Gestión de Inventario", font=("Segoe UI", 9), bg='white', fg='#7F8C8D').pack(pady=(5, 20))
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)
        
        # Formulario
        frame_form = tk.Frame(frame, bg='white')
        frame_form.pack(pady=15)
        
        tk.Label(frame_form, text="Usuario", font=("Segoe UI", 10), bg='white').pack(anchor=tk.W, padx=20)
        self.entry_usuario = tk.Entry(frame_form, font=("Segoe UI", 11), bg='#F8F9FA', relief=tk.FLAT, bd=1, width=25)
        self.entry_usuario.pack(fill=tk.X, padx=20, pady=(5, 15))
        self.entry_usuario.insert(0, "admin")
        
        tk.Label(frame_form, text="Contraseña", font=("Segoe UI", 10), bg='white').pack(anchor=tk.W, padx=20)
        self.entry_password = tk.Entry(frame_form, show="•", font=("Segoe UI", 11), bg='#F8F9FA', relief=tk.FLAT, bd=1, width=25)
        self.entry_password.pack(fill=tk.X, padx=20, pady=(5, 10))
        self.entry_password.insert(0, "admin123")
        
        # Mostrar contraseña
        self.show_password = tk.BooleanVar(value=False)
        tk.Checkbutton(frame_form, text="Mostrar contraseña", variable=self.show_password,
                      command=self._toggle_password, bg='white', font=("Segoe UI", 9)).pack(anchor=tk.W, padx=20)
        
        self.lbl_error = tk.Label(frame, text="", bg='white', fg='#E74C3C', font=("Segoe UI", 9))
        self.lbl_error.pack(pady=5)
        
        btn_login = tk.Button(frame, text="INGRESAR", command=self._login,
                              bg='#3498DB', fg='white', font=("Segoe UI", 11, "bold"),
                              relief=tk.FLAT, padx=30, pady=10, cursor='hand2')
        btn_login.pack(pady=15)
        
        # Hover effect
        btn_login.bind('<Enter>', lambda e: btn_login.config(bg='#2980B9'))
        btn_login.bind('<Leave>', lambda e: btn_login.config(bg='#3498DB'))
        
        tk.Label(frame, text="© 2024 - Sistema Profesional", font=("Segoe UI", 8), bg='white', fg='#95A5A6').pack(side=tk.BOTTOM, pady=10)
    
    def _configurar_eventos(self):
        """
        Configura los atajos de teclado y el foco inicial en los campos de entrada.
        """
        self.window.bind('<Return>', lambda e: self._login())
        self.entry_usuario.focus()
    
    def _toggle_password(self):
        """
        Muestra u oculta la contraseña en texto plano según la opción seleccionada.
        """
        if self.show_password.get():
            self.entry_password.config(show="")
        else:
            self.entry_password.config(show="•")
    
    def _login(self):
        """
        Realiza el proceso de validación de las credenciales ingresadas.

        Verifica si el usuario y la contraseña ingresados coinciden con la cuenta
        de administrador. Si es correcto, inicia la `MainWindow`.
        """
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get()
        
        if not usuario:
            self.lbl_error.config(text="❌ Ingrese su usuario")
            return
        if not password:
            self.lbl_error.config(text="❌ Ingrese su contraseña")
            return
        
        if usuario == "admin" and password == "admin123":
            self.lbl_error.config(text="✅ Acceso concedido...", fg='#28A745')
            self.window.update()
            
            usuario_obj = {
                'id_usuario': 1,
                'nombre_usuario': 'admin',
                'nombre_completo': 'Administrador',
                'rol_nombre': 'Administrador'
            }
            
            self.window.destroy()
            
            try:
                from vistas.main_window import MainWindow
                MainWindow(usuario_obj)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo iniciar: {str(e)}")
        else:
            self.lbl_error.config(text="❌ Usuario o contraseña incorrectos", fg='#E74C3C')
            self.entry_password.delete(0, tk.END)

if __name__ == "__main__":
    LoginWindow()