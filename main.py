import threading
from datos import STOCK_INICIAL, PEDIDOS, REPOSICIONES, NUM_CAJAS, NUM_TERMINALES, NUM_REVISORES
from inventario import GestorInventario
from hilos import Caja, Almacen, Revisor
 
 
def main():
    gestor = GestorInventario(STOCK_INICIAL)
    terminales = threading.Semaphore(NUM_TERMINALES)
 
    cajas = []
    for i in range(NUM_CAJAS):
        mis_pedidos = PEDIDOS[i::NUM_CAJAS]
        cajas.append(Caja(f"caja-{i + 1}", mis_pedidos, terminales, gestor))
    almacen = Almacen(REPOSICIONES, gestor)
 
    print("--- VENTAS Y REPOSICIONES ---")
    for caja in cajas:
        caja.start()
    almacen.start()
    for caja in cajas:
        caja.join()
    almacen.join()
 
    print("\n--- REVISIÓN FINAL ---")
    productos = gestor.productos()
    barrera = threading.Barrier(NUM_REVISORES)
    revisores = []
    for i in range(NUM_REVISORES):
        mis_productos = productos[i::NUM_REVISORES]
        revisores.append(Revisor(f"revisor-{i + 1}", mis_productos, barrera, gestor))
 
    for revisor in revisores:
        revisor.start()
    for revisor in revisores:
        revisor.join()
 
    print("\nSTOCK FINAL")
    for producto, unidades in gestor.resumen().items():
        print(f"  {producto}: {unidades}")
 
 
if __name__ == "__main__":
    main()