import threading
from datos import PEDIDOS, NUM_CAJAS, NUM_TERMINALES
from inventario import inventario
from hilos import Caja
 
 
def main():
    semaforo_terminales = threading.Semaphore(NUM_TERMINALES)
 
    cajas = []
    for i in range(NUM_CAJAS):
        mis_pedidos = PEDIDOS[i::NUM_CAJAS]
        cajas.append(Caja(f"caja-{i + 1}", mis_pedidos, semaforo_terminales))
 
    for caja in cajas:
        caja.start()
    for caja in cajas:
        caja.join()
 
    print("\nSTOCK FINAL")
    for producto, unidades in inventario.items():
        print(f"  {producto}: {unidades}")
 
 
if __name__ == "__main__":
    main()