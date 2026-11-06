import threading
from datos import PEDIDOS, REPOSICIONES, NUM_CAJAS, NUM_TERMINALES, NUM_REVISORES
from inventario import inventario
from hilos import Caja, Almacen, Revisor
 
 
def main():
    terminales = threading.Semaphore(NUM_TERMINALES)
 
    cajas = []
    for i in range(NUM_CAJAS):
        mis_pedidos = PEDIDOS[i::NUM_CAJAS]
        cajas.append(Caja(f"caja-{i + 1}", mis_pedidos, terminales))
    almacen = Almacen(REPOSICIONES)
 
    print("--- VENTAS Y REPOSICIONES ---")
    for caja in cajas:
        caja.start()
    almacen.start()
    for caja in cajas:
        caja.join()
    almacen.join()
 
    print("\n--- REVISIÓN FINAL ---")
    productos = list(inventario)
    barrera = threading.Barrier(NUM_REVISORES)
    revisores = []
    for i in range(NUM_REVISORES):
        mis_productos = productos[i::NUM_REVISORES]
        revisores.append(Revisor(f"revisor-{i + 1}", mis_productos, barrera))
 
    for revisor in revisores:
        revisor.start()
    for revisor in revisores:
        revisor.join()
 
    print("\nSTOCK FINAL")
    for producto, unidades in inventario.items():
        print(f"  {producto}: {unidades}")
 
 
if __name__ == "__main__":
    main()