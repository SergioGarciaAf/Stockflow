import threading
from inventario import vender
 
class Caja(threading.Thread):
    def __init__(self, nombre, pedidos):
        super().__init__(name=nombre)
        self.pedidos = list(pedidos)
 
    def run(self): # lo que hace el hilo cuando se inicia 
        for numero_pedido, producto, unidades in self.pedidos:
            vender(self.name, numero_pedido, producto, unidades)