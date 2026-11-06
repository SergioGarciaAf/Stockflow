import threading
from datos import NUM_CAJAS
from inventario import inventario, vender
 
PRODUCTO = "Router WiFi"
 
print(f"Hay {inventario[PRODUCTO]} unidades de {PRODUCTO}")
print(f"{NUM_CAJAS} cajas piden 2 cada una a la vez\n")
 
hilos = []
for i in range(NUM_CAJAS):
    h = threading.Thread(target=vender, args=(f"caja-{i + 1}", f"PRUEBA-{i + 1}", PRODUCTO, 2))
    hilos.append(h)
 
for h in hilos:
    h.start()
for h in hilos:
    h.join()