import threading
import time
 
 
class Caja(threading.Thread):
    def __init__(self, nombre, pedidos, terminales, gestor):
        super().__init__(name=nombre)
        self.pedidos = list(pedidos)
        self.terminales = terminales
        self.gestor = gestor
 
    def run(self):
        for numero_pedido, producto, unidades in self.pedidos:
            print(f"[{self.name}] espero terminal para {numero_pedido}")
            with self.terminales:
                print(f"[{self.name}] COJO terminal")
                self.gestor.vender(self.name, numero_pedido, producto, unidades)
                time.sleep(1.0)
                print(f"[{self.name}] SUELTO terminal")
 
 
class Almacen(threading.Thread):
    def __init__(self, reposiciones, gestor):
        super().__init__(name="almacen")
        self.reposiciones = list(reposiciones)
        self.gestor = gestor
 
    def run(self):
        for numero_albaran, producto, unidades in self.reposiciones:
            self.gestor.reponer(self.name, numero_albaran, producto, unidades)
            time.sleep(2.0)

 
class Revisor(threading.Thread):
    def __init__(self, nombre, productos, barrera, gestor):
        super().__init__(name=nombre)
        self.productos = list(productos)
        self.barrera = barrera
        self.gestor = gestor
 
    def run(self):
        for producto in self.productos:
            print(f"[{self.name}] {producto}: {self.gestor.consultar(producto)}")
        print(f"[{self.name}] he terminado mi parte -> espero en la barrera")
        self.barrera.wait()
        print(f"[{self.name}] barrera superada")

class Cancelaciones(threading.Thread):
    def __init__(self, cancelaciones,gestor):
        super().__init__(name="cancelaciones")
        self.cancelaciones = cancelaciones
        self.gestor = gestor

    def run(self):
        for numero_cancelacion,numero_pedido,tiempo in self.cancelaciones:
            self.gestor.cancelar(numero_pedido)
            time.sleep(tiempo)

