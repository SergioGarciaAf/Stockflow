import threading
import time
from datos import STOCK_INICIAL
 
inventario = dict(STOCK_INICIAL)
lock = threading.Lock()
condicion = threading.Condition(lock)
 
 
def vender(caja, numero_pedido, producto, unidades, esperar=True):
    with condicion:
        while inventario[producto] < unidades and esperar:
            print(f"[{caja}] {numero_pedido}: espero reposición de {producto} (hay {inventario[producto]}, pide {unidades})")
            condicion.wait()
 
        disponible = inventario[producto]
        if disponible >= unidades:
            time.sleep(0.05)
            inventario[producto] = disponible - unidades
            vendido = True
        else:
            vendido = False
        quedan = inventario[producto]
 
    if vendido:
        print(f"[{caja}] {numero_pedido}: vendo {unidades} x {producto} -> quedan {quedan}")
    else:
        print(f"[{caja}] {numero_pedido}: NO hay bastante {producto} (hay {quedan}, pide {unidades})")
    return vendido
 
 
def reponer(quien, numero_albaran, producto, unidades):
    with condicion:
        inventario[producto] += unidades
        hay = inventario[producto]
        condicion.notify_all()
    print(f"[{quien}] {numero_albaran}: repongo {unidades} x {producto} -> hay {hay}")