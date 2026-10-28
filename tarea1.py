
import threading
import time
from datos import STOCK_INICIAL, PEDIDOS, NUM_CAJAS


inventario = STOCK_INICIAL.copy()


ventas_realizadas = 0
ventas_rechazadas = 0


def procesar_pedido(pedido, numero_caja):
    global ventas_realizadas, ventas_rechazadas

    id_pedido = pedido["id"]
    producto = pedido["producto"]
    cantidad = pedido["cantidad"]

    if producto not in inventario:
        print(
            f"[Caja {numero_caja}] "
            f"Pedido {id_pedido} rechazado: producto inexistente."
        )
        ventas_rechazadas += 1
        return

    stock_actual = inventario[producto]

    time.sleep(0.01)

    if stock_actual >= cantidad:

        inventario[producto] -= cantidad

        print(
            f"[Caja {numero_caja}] "
            f"Pedido {id_pedido} vendido: "
            f"{cantidad} unidades de {producto}. "
            f"Stock restante: {inventario[producto]}"
        )

        ventas_realizadas += 1

    else:
        print(
            f"[Caja {numero_caja}] "
            f"Pedido {id_pedido} rechazado: "
            f"stock insuficiente de {producto}. "
            f"Disponible: {inventario[producto]}, "
            f"solicitado: {cantidad}"
        )

        ventas_rechazadas += 1


def trabajador_caja(numero_caja, pedidos, siguiente_pedido, cerrojo_reparto):
    """
    Cada hilo representa una caja.

    Los pedidos se reparten entre las cajas utilizando un cerrojo
    para proteger únicamente el reparto de la lista.

    El acceso al inventario NO está protegido por ningún Lock.
    """
    while True:
        with cerrojo_reparto:
            if siguiente_pedido[0] >= len(pedidos):
                return

            pedido = pedidos[siguiente_pedido[0]]
            siguiente_pedido[0] += 1

        procesar_pedido(pedido, numero_caja)


def main():
    print("=" * 60)
    print("STOCKFLOW - FASE 1: CONDICIÓN DE CARRERA")
    print("=" * 60)

    print(f"Número de cajas: {NUM_CAJAS}")
    print(f"Número de pedidos: {len(PEDIDOS)}")
    print("\nStock inicial:")



if __name__ == "__main__":
    main()
