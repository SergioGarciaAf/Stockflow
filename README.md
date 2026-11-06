# StockFlow
 
## Descripción
 
StockFlow simula una tienda en la que varias **cajas** venden pedidos **a la vez** sobre un **mismo inventario**. Cada caja es un hilo (`threading.Thread`). Como todas las cajas leen y cambian el mismo stock, pueden aparecer problemas de concurrencia.
 
El proyecto se hace por fases: primero se programa **sin sincronización**, para ver el fallo, y después se va corrigiendo con `Lock`, `Semaphore`, `Condition`, `Barrier` y `RLock`.
 
> Estado actual: **Fase 1** (condición de carrera, sin ningún Lock).
 
## Cómo ejecutarlo
 
Necesitas Python 3 (yo uso Python 3.14 en Windows). Desde la carpeta del proyecto:
 
```powershell
py main.py              # las 6 cajas procesan los 40 pedidos
py prueba_carrera.py    # prueba que provoca la condición de carrera
```
 
## Estructura de archivos
 
```text
stockflow/
├── datos.py             # datos de partida del profesor (no se modifica)
├── inventario.py        # el inventario compartido y la función vender()
├── hilos.py             # la clase Caja (un hilo que procesa sus pedidos)
├── main.py              # reparte los pedidos, crea las 6 cajas, las lanza y las espera
├── prueba_carrera.py    # 6 cajas compiten por el mismo producto a la vez
├── README.md
└── .gitignore
```
 
## Fase 1 · Condición de carrera
 
### Qué hace el programa
 
- **Inventario:** `inventario = dict(STOCK_INICIAL)`. Es una **copia** del diccionario de `datos.py`, para no tocar el original. Es el **recurso compartido**: todas las cajas lo usan.
- **Cajas:** la clase `Caja` hereda de `threading.Thread`. Cada caja recibe su lista de pedidos y en `run()` los vende uno a uno.
- **Reparto de pedidos:** en `main.py`, la caja `i` se lleva `PEDIDOS[i::NUM_CAJAS]` (uno de cada seis, como repartir cartas). Así las cajas 1 a 4 tienen 7 pedidos y las cajas 5 y 6 tienen 6.
- **main:** primero hace `start()` de las 6 cajas y después `join()` de las 6, en dos bucles separados, para que trabajen a la vez. Al final muestra el stock.
- **vender():** lee cuántas unidades hay, comprueba si llegan y, si llegan, las descuenta. En esta fase **no hay ningún Lock**.
### La sección crítica
 
La sección crítica de `vender()` son estas líneas:
 
```python
disponible = inventario[producto]                 # 1. leer
if disponible >= unidades:                        # 2. comprobar
    time.sleep(0.05)                              #    (ventana de carrera)
    inventario[producto] = disponible - unidades  # 3. descontar
```
 
Leer, comprobar y descontar tienen que hacerse **de una vez y de una caja en una**. Si dos cajas ejecutan estas líneas a la vez, las dos pueden leer el mismo valor, las dos creen que hay stock y las dos venden.
 
El `time.sleep(0.05)` entre comprobar y descontar está **a propósito**: hace más grande el hueco en el que otra caja se puede colar, para que el fallo se vea. No forma parte de una solución real.
 
### Prueba: provocar la carrera (`prueba_carrera.py`)
 
Hay **6 Router WiFi**, y **6 cajas piden 2 cada una, a la vez**.
 
- **Lo que debería pasar:** venden 3 cajas (quedan 4, 2 y 0) y las otras 3 dicen «NO hay bastante». Stock final: **0**.
- **Lo que pasa sin Lock:**
> **Pon aquí tu salida.** Copia lo que te sale al ejecutar `py prueba_carrera.py` y borra este aviso. Debería salir algo como esto:
 
```text
Hay 6 unidades de Router WiFi
6 cajas piden 2 cada una a la vez
 
[caja-1] PRUEBA-1: vendo 2 x Router WiFi -> quedan 4
[caja-2] PRUEBA-2: vendo 2 x Router WiFi -> quedan 4
[caja-3] PRUEBA-3: vendo 2 x Router WiFi -> quedan 4
[caja-4] PRUEBA-4: vendo 2 x Router WiFi -> quedan 4
[caja-5] PRUEBA-5: vendo 2 x Router WiFi -> quedan 4
[caja-6] PRUEBA-6: vendo 2 x Router WiFi -> quedan 4
 
Stock final de Router WiFi: 4
```
 
Las 6 cajas venden. Hay **dos errores** a la vez:
 
1. Se venden **12 routers** cuando solo había 6.
2. El stock final dice **4**, cuando tendría que ser 0 (y con 12 vendidos ni siquiera cuadraría).
Así pasa, momento a momento:
 
| Momento | caja-1 | caja-2 | Stock |
|---|---|---|---|
| 1 | lee 6 | | 6 |
| 2 | | lee 6 | 6 |
| 3 | 6 ≥ 2, sí hay | 6 ≥ 2, sí hay | 6 |
| 4 | (espera 0,05 s) | (espera 0,05 s) | 6 |
| 5 | escribe 6 − 2 = 4 | | 4 |
| 6 | | escribe 6 − 2 = 4 | **4** |
 
Ninguna caja ve lo que hizo la otra, porque todas calcularon a partir del 6 que leyeron al principio. Esto es una **condición de carrera**: el resultado depende del orden en que los hilos llegan al recurso compartido.
 
> **Pon aquí cuántas veces lo has ejecutado** (por ejemplo: «Lo he ejecutado 3 veces y las 3 ha salido stock final 4»).
 
### ¿Por qué en `main.py` casi nunca se ve el fallo?
 
Al ejecutar `py main.py` varias veces, el stock final sale bien: 39 ventas, y PED-040 se rechaza porque pide 4 Router WiFi y solo quedan 3. Con el reparto «de uno en uno», en cada momento las 6 cajas suelen estar vendiendo productos **distintos**, así que es muy difícil que dos coincidan sobre el mismo producto a la vez.
 
Que no se vea **no significa que esté bien**: la carrera es posible, pero depende de la casualidad. Por eso hace falta una prueba aparte (`prueba_carrera.py`) que la provoque siempre.
 
> **Pon aquí cuántas veces has ejecutado `main.py`** y qué te ha salido.
 
### Conclusión
 
Hace falta que leer, comprobar y descontar se hagan como **una sola operación**, y que solo una caja pueda estar ahí dentro a la vez (**exclusión mutua**). Eso se arregla en la fase 2 con un `Lock`.
 
## Pruebas realizadas
 
| Prueba | Cómo la hago | Resultado |
|---|---|---|
| Mostrar una condición de carrera antes de sincronizar | `py prueba_carrera.py` (varias veces) | Las 6 cajas venden 2 routers cuando solo había 6, y el stock final es 4 en vez de 0. El fallo aparece, como se esperaba en esta fase. |
| Ejecutar la aplicación varias veces | `py main.py` (varias veces) | 39 ventas y 1 rechazo (PED-040). Con este reparto el fallo casi nunca se ve. |