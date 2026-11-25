import threading
import time
 
 
class Caja(threading.Thread):
    def __init__(self, nombre, pedidos, terminales, gestor,evento):
        super().__init__(name=nombre)
        self.pedidos = list(pedidos)
        self.terminales = terminales
        self.gestor = gestor
        self.evento = evento
        self.lista = [self.name,[],[],[]]
        self.bandera = "nada"
 
    def run(self):
        for numero_pedido, producto, unidades in self.pedidos:
            self.evento.wait()
            self.bandera = "esperando"
            self.lista[2].append(numero_pedido)
            if self.bandera == "esperando":
                self.lista[3].append(numero_pedido)
            elif self.bandera == "nada":
                self.lista[1].append(numero_pedido)
            print(f"[{self.name}] espero terminal para {numero_pedido}")
            with self.terminales:
                print(f"[{self.name}] COJO terminal")
                self.gestor.vender(self.name, numero_pedido, producto, unidades)
                time.sleep(0.1)
                print(f"[{self.name}] SUELTO terminal")
 
 
class Almacen(threading.Thread):
    def __init__(self, reposiciones, gestor):
        super().__init__(name="almacen")
        self.reposiciones = list(reposiciones)
        self.gestor = gestor
 
    def run(self):
        time.sleep(1.5)
        for numero_albaran, producto, unidades in self.reposiciones:
            self.gestor.reponer(self.name, numero_albaran, producto, unidades)
            time.sleep(0.3)
 
 
class Revisor(threading.Thread):
    def __init__(self, nombre, productos, barrera, gestor):
        super().__init__(name=nombre)
        self.productos = list(productos)
        self.barrera = barrera
        self.gestor = gestor
 
    def run(self):
        for producto in self.productos:
            print(f"[{self.name}] {producto}: {self.gestor.consultar(producto)}")
            time.sleep(0.1)
        print(f"[{self.name}] he terminado mi parte -> espero en la barrera")
        self.barrera.wait()
        print(f"[{self.name}] barrera superada")

class Pausa(threading.Thread):
    def __init__(self, gestor,evento):
        super().__init__(name="Pausa")
        self.gestor = gestor
        self.evento = evento

    def run(self):
        self.gestor.pausa(self.evento)