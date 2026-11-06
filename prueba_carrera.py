import threading
from datos import STOCK_INICIAL, NUM_CAJAS
from inventario import GestorInventario
 
PRODUCTO = "Router WiFi"
gestor = GestorInventario(STOCK_INICIAL)
 
print(f"Hay {gestor.consultar(PRODUCTO)} unidades de {PRODUCTO}")
print(f"{NUM_CAJAS} cajas piden 2 cada una a la vez\n")
 
hilos = []
for i in range(NUM_CAJAS):
    h = threading.Thread(target=gestor.vender, args=(f"caja-{i + 1}", f"PRUEBA-{i + 1}", PRODUCTO, 2, False))
    hilos.append(h)
 
for h in hilos:
    h.start()
for h in hilos:
    h.join()
 
print(f"\nStock final de {PRODUCTO}: {gestor.consultar(PRODUCTO)}")