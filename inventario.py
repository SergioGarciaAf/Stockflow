import threading
import time
from datos import STOCK_INICIAL
 
inventario = dict(STOCK_INICIAL)
lock = threading.Lock()
 
 
def vender(caja, numero_pedido, producto, unidades):
    with lock:
        # Accedemos al inventario y vemos del producto cuanto queda disponible
        disponible = inventario[producto]
        
        #Si hay stock 
        if disponible >= unidades:
            time.sleep(0.05)
            #descontamos el producto
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