import threading
from datos import STOCK_INICIAL, PEDIDOS, REPOSICIONES, NUM_CAJAS, NUM_TERMINALES, NUM_REVISORES, CANCELACIONES
from inventario import GestorInventario
from hilos import Caja, Almacen, Revisor,Cancelaciones
 
 
def main():
    terminales = threading.Semaphore(NUM_TERMINALES)
    diccionario_pedido = {}
    for numero_pedido,produto,cantidad in PEDIDOS:
        diccionario_pedido[numero_pedido] = "Pendiente"
    gestor = GestorInventario(STOCK_INICIAL,diccionario_pedido)

    cajas = []
    for i in range(NUM_CAJAS):
        mis_pedidos = PEDIDOS[i::NUM_CAJAS] 
        cajas.append(Caja(f"caja-{i + 1}", mis_pedidos, terminales, gestor))
    almacen = Almacen(REPOSICIONES, gestor)
    cancelaciones = Cancelaciones(CANCELACIONES,gestor)

    print("--- VENTAS Y REPOSICIONES ---")
    for caja in cajas:
        caja.start()
    almacen.start()
    cancelaciones.start()
    for caja in cajas:
        caja.join()
    almacen.join()
    cancelaciones.join()
 
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

    print("Cancelaciones")
    print("rechazados")
    for pedido in gestor.lista_pedidos_rechazados:
        print(pedido)
    print("no rechazados")
    for pedido in gestor.lista_pedidos_aceptados:
        print(pedido)
    
    for clave,valor in diccionario_pedido.items():
        print(f"{clave},{valor}")
    print("lista pedidos que no existen ")
    print(gestor.lista_pedidos_no_existen)
 
 
if __name__ == "__main__":
    main()