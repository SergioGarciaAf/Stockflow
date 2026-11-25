import threading
import time


class GestorInventario:
    def __init__(self, stock_inicial):
        self._stock = dict(stock_inicial)
        self._lock = threading.RLock()
        self._condicion = threading.Condition(self._lock)
        self.evento = threading.Event()

    def consultar(self, producto):
        with self._lock:
            return self._stock[producto]

    def vender(self, caja, numero_pedido, producto, unidades, esperar=True):
        with self._condicion:
            while self._stock[producto] < unidades and esperar:
                print(f"[{caja}] {numero_pedido}: espero reposición de {producto} (hay {self._stock[producto]}, pide {unidades})")
                self._condicion.wait()

            disponible = self._stock[producto]
            if disponible >= unidades:
                self._stock[producto] = disponible - unidades
                vendido = True
            else:
                vendido = False
            quedan = self._stock[producto]

        if vendido:
            print(f"[{caja}] {numero_pedido}: vendo {unidades} x {producto} -> quedan {quedan}")
        else:
            print(f"[{caja}] {numero_pedido}: NO hay bastante {producto} (hay {quedan}, pide {unidades})")
        return vendido

    def reponer(self, quien, numero_albaran, producto, unidades):
        with self._condicion:
            self._stock[producto] += unidades
            hay = self._stock[producto]
            self._condicion.notify_all()
        print(f"[{quien}] {numero_albaran}: repongo {unidades} x {producto} -> hay {hay}")

    def productos(self):
        with self._lock:
            return list(self._stock)

    def resumen(self):
        with self._lock:
            copia = {}
            for producto in self._stock:
                copia[producto] = self.consultar(producto)
            return copia

    def pausa(self,evento):
        time.sleep(3)
        evento.clear()
        time.sleep(4)
        evento.set()