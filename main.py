import threading
from datos import STOCK_INICIAL, PEDIDOS, REPOSICIONES, NUM_CAJAS, NUM_TERMINALES, NUM_REVISORES
from inventario import GestorInventario
from hilos import Caja, Almacen, Revisor,Pausa
 
 
def main():
    gestor = GestorInventario(STOCK_INICIAL)
    terminales = threading.Semaphore(NUM_TERMINALES)
    evento = threading.Event()
    evento.set()
 
    cajas = []
    for i in range(NUM_CAJAS):
        mis_pedidos = PEDIDOS[i::NUM_CAJAS]
        cajas.append(Caja(f"caja-{i + 1}", mis_pedidos, terminales, gestor,evento))
    almacen = Almacen(REPOSICIONES, gestor)
    pausa = Pausa(gestor,evento)

 
    print("--- VENTAS Y REPOSICIONES ---")
    for caja in cajas:
        caja.start()
    almacen.start()
    pausa.start()

    for caja in cajas:
        caja.join()
    almacen.join()
    pausa.join()
 
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

    for caja in cajas:
        print("Resumen")
        print(f"nombre {caja.lista[0]}")
        print(f"antes {caja.lista[1]}")
        print(f"en curso {caja.lista[2]}")
        print(f"tras reanudar {caja.lista[3]}")
 
 
if __name__ == "__main__":
    main()