# utils/eventos.py
# -*- coding: utf-8 -*-

class Eventos:
    """Sistema de eventos para actualizar vistas en tiempo real"""
    
    _observadores = {}
    
    @classmethod
    def suscribir(cls, evento, callback):
        """Suscribe un callback a un evento"""
        if evento not in cls._observadores:
            cls._observadores[evento] = []
        cls._observadores[evento].append(callback)
    
    @classmethod
    def notificar(cls, evento, datos=None):
        """Notifica a todos los observadores de un evento"""
        if evento in cls._observadores:
            for callback in cls._observadores[evento]:
                try:
                    if datos:
                        callback(datos)
                    else:
                        callback()
                except Exception as e:
                    print(f"Error en callback: {e}")
    
    @classmethod
    def limpiar(cls):
        """Limpia todos los observadores"""
        cls._observadores = {}

# Eventos disponibles
EVENTO_STOCK_ACTUALIZADO = "stock_actualizado"
EVENTO_VENTA_REGISTRADA = "venta_registrada"
EVENTO_PRODUCTO_AGREGADO = "producto_agregado"
EVENTO_PRODUCTO_EDITADO = "producto_editado"
EVENTO_PEDIDO_CREADO = "pedido_creado"