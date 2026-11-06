import time
from datos import STOCK_INICIAL

# crea un diccionario que no es el original 
inventario = dict(STOCK_INICIAL) 

def vender(caja,numero_pedido,producto,unidades):
    # Accedemos al inventario y vemos delproducto cuanto queda disponible
    disponible = inventario[producto]
    #Si hay stock 
    if disponible >= unidades: 
        time.sleep(0.05)
        #descontamos el producto 
        inventario[producto] = disponible -unidades 
        
        print(f"[{caja}] {numero_pedido}: vendo {unidades} x {producto} quedan {inventario[producto]}")
        return True
    print(f"[{caja}] {numero_pedido}: NO hay bastante {producto} (hay {disponible})")
    return False