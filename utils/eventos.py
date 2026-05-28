# utils/eventos.py
# -*- coding: utf-8 -*-

class Eventos:
    """
    Módulo observador-sujeto que permite comunicar cambios en el sistema 
    sin acoplamiento directo entre módulos.

    Los controladores notifican eventos
    y las interfaces (vistas) se suscriben para actualizarse automáticamente.
    """
    
    _observadores = {}
    
    @classmethod
    def suscribir(cls, evento, callback):
        """
        Suscribe un callback a un evento
        Args:
            evento (str): Nombre del evento al que se suscribe.
            callback (function): Función a ejecutar cuando se notifique el evento.
        """
        if evento not in cls._observadores:
            cls._observadores[evento] = []
        cls._observadores[evento].append(callback)
    
    @classmethod
    def notificar(cls, evento, datos=None):
        """
        Notifica a todos los observadores de un evento
        Args:
            evento (str): Nombre del evento a notificar.
            datos (any, optional): Datos adicionales a pasar a los callbacks.
        """
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
        """
        Limpia todos los observadores
        """
        cls._observadores = {}

# Eventos disponibles
EVENTO_STOCK_ACTUALIZADO = "stock_actualizado"
EVENTO_VENTA_REGISTRADA = "venta_registrada"
EVENTO_PRODUCTO_AGREGADO = "producto_agregado"
EVENTO_PRODUCTO_EDITADO = "producto_editado"
EVENTO_PEDIDO_CREADO = "pedido_creado"