import threading
import time
from inventario import vender
 
 
class Caja(threading.Thread):
    def __init__(self, nombre, pedidos, terminales):
        super().__init__(name=nombre)
        self.pedidos = list(pedidos)
        self.terminales = terminales
 
    def run(self):
        for numero_pedido, producto, unidades in self.pedidos:
            print(f"[{self.name}] espero terminal para {numero_pedido}")
            # Espero aqui hasta que haya 3 libre 
            with self.terminales:
                print(f"[{self.name}] COJO terminal")# pilla una terminal disponible 
                vender(self.name, numero_pedido, producto, unidades)
                time.sleep(0.1)
                print(f"[{self.name}] SUELTO terminal")