import threading
import time
from inventario import vender, reponer, consultar
 
 
class Caja(threading.Thread):
    def __init__(self, nombre, pedidos, terminales):
        super().__init__(name=nombre)
        self.pedidos = list(pedidos)
        self.terminales = terminales
 
    def run(self):
        for numero_pedido, producto, unidades in self.pedidos:
            print(f"[{self.name}] espero terminal para {numero_pedido}")
            with self.terminales:
                print(f"[{self.name}] COJO terminal")
                vender(self.name, numero_pedido, producto, unidades)
                time.sleep(0.1)
                print(f"[{self.name}] SUELTO terminal")
 
 
class Almacen(threading.Thread):
    def __init__(self, reposiciones):
        super().__init__(name="almacen")
        self.reposiciones = list(reposiciones)
 
    def run(self):
        time.sleep(1.5)
        for numero_albaran, producto, unidades in self.reposiciones:
            reponer(self.name, numero_albaran, producto, unidades)
            time.sleep(0.3)
            
class Revisor(threading.Thread):
    def __init__(self, nombre, productos, barrera):
        super().__init__(name=nombre)
        self.productos = list(productos)
        self.barrera = barrera
 
    def run(self):
        for producto in self.productos:
            print(f"[{self.name}] {producto}: {consultar(producto)}")
            time.sleep(0.1)
        print(f"[{self.name}] he terminado mi parte -> espero en la barrera")
        self.barrera.wait()
        print(f"[{self.name}] barrera superada")