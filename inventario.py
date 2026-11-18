import threading
import time


class GestorInventario:
    def __init__(self, stock_inicial,diccionario_pedido):
        self._stock = dict(stock_inicial)
        self._lock = threading.RLock()
        self._condicion = threading.Condition(self._lock)
        self.diccionario_pedido = diccionario_pedido
        self.lista_pedidos_aceptados = []
        self.lista_pedidos_rechazados = []
        self.lista_pedidos_no_existen = []
        self.bandera = False

    def consultar(self, producto):
        with self._lock:
            return self._stock[producto]

    def vender(self, caja, numero_pedido, producto, unidades, esperar=True):
        with self._condicion:
            while self._stock[producto] < unidades and esperar:
                print(f"[{caja}] {numero_pedido}: espero reposición de {producto} (hay {self._stock[producto]}, pide {unidades})")
                self.diccionario_pedido[numero_pedido] = "Esperando stock"
                self._condicion.wait()

            disponible = self._stock[producto]
            if disponible >= unidades:
                self.diccionario_pedido[numero_pedido] = "En cobro"
                self._stock[producto] = disponible - unidades
                vendido = True
                self.diccionario_pedido[numero_pedido] = "vendido"
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

    def cancelar(self,numero_pedido):
        with self._lock:
            for clave ,valor in self.diccionario_pedido.items():
                if clave == numero_pedido:
                    self.bandera = True

            if self.bandera == False:
                self.lista_pedidos_no_existen.append(numero_pedido)
            if self.bandera == True:
                numero_pedidos = self.diccionario_pedido[numero_pedido]

                if  numero_pedidos == "Pendiente" or numero_pedidos == "Esperando_stock":
                    self.diccionario_pedido[numero_pedido] = "Cancelado"
                    self.lista_pedidos_aceptados.append(numero_pedido)
                else:
                    self.lista_pedidos_rechazados.append(numero_pedido)
            

