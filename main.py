import threading
from datos import PEDIDOS, REPOSICIONES, NUM_CAJAS, NUM_TERMINALES
from inventario import inventario
from hilos import Caja, Almacen
 
 
def main():
    terminales = threading.Semaphore(NUM_TERMINALES)
 
    cajas = []
    for i in range(NUM_CAJAS):
        mis_pedidos = PEDIDOS[i::NUM_CAJAS]
        cajas.append(Caja(f"caja-{i + 1}", mis_pedidos, terminales))
    almacen = Almacen(REPOSICIONES)
 
    for caja in cajas:
        caja.start()
    almacen.start()
 
    for caja in cajas:
        caja.join()
    almacen.join()
 
    print("\nSTOCK FINAL")
    for producto, unidades in inventario.items():
        print(f"  {producto}: {unidades}")
 
 
if __name__ == "__main__":
    main()