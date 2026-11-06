# StockFlow

## Descripción

StockFlow simula una tienda en la que varias **cajas** venden pedidos **a la vez** sobre un **mismo inventario**. Cada caja es un hilo (`threading.Thread`). Como todas las cajas leen y cambian el mismo stock, pueden aparecer problemas de concurrencia.

El proyecto se hace por fases: primero se programa **sin sincronización**, para ver el fallo, y después se va corrigiendo con `Lock`, `Semaphore`, `Condition`, `Barrier` y `RLock`.

> Estado actual: **Fase 2** (el inventario está protegido con un `Lock`).

## Cómo ejecutarlo

Necesitas Python 3 (yo uso Python 3.14 en Windows). Desde la carpeta del proyecto:

```powershell
py main.py              # las 6 cajas procesan los 40 pedidos
py prueba_carrera.py    # 6 cajas compiten a la vez por el mismo producto
```

## Estructura de archivos

```text
stockflow/
├── datos.py             # datos de partida del profesor (no se modifica)
├── inventario.py        # el inventario compartido, su Lock y la función vender()
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
- **Lo que pasa sin Lock** (con el código de la fase 1; desde la fase 2, esta misma prueba ya sale bien):

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

## Fase 2 · Protección con Lock

### Qué he cambiado

Solo cambia `inventario.py`:

```python
lock = threading.Lock()          # UN cerrojo para todas las cajas

def vender(caja, numero_pedido, producto, unidades):
    with lock:                                           # coge el cerrojo
        disponible = inventario[producto]                # 1. leer
        if disponible >= unidades:                       # 2. comprobar
            time.sleep(0.05)
            inventario[producto] = disponible - unidades # 3. descontar
            vendido = True
        else:
            vendido = False
        quedan = inventario[producto]
                                                         # aquí suelta el cerrojo
    if vendido:
        print(...)   # los print van FUERA del with
    else:
        print(...)
    return vendido
```

### Para qué sirve el Lock

Un `Lock` es un cerrojo con **una sola llave**: la caja que la coge entra en la sección crítica y las demás esperan en la puerta hasta que salga. Eso es la **exclusión mutua**: solo una caja puede estar leyendo, comprobando y descontando a la vez.

Uso `with lock:` en vez de `lock.acquire()` y `lock.release()` porque el `with` suelta el cerrojo solo al salir del bloque, **aunque salte un error**. Si un cerrojo se quedara cogido, las demás cajas esperarían para siempre.

### Decisiones importantes

- **El Lock se crea una sola vez, fuera de la función.** Tiene que ser el **mismo** cerrojo para todas las cajas. Si lo creara dentro de `vender()`, cada llamada tendría su propio cerrojo y no protegería nada.
- **Comprobar y descontar van dentro del mismo `with`.** Si solo protegiera el descuento, dos cajas podrían comprobar a la vez «hay 6» antes de que ninguna descontara, y las dos venderían igualmente. Lo que hay que proteger es la operación entera.
- **Los `print` van fuera del `with`.** No tocan el inventario, así que no necesitan el cerrojo. Si estuvieran dentro, las demás cajas esperarían más tiempo para nada. Por eso guardo el resultado en `vendido` y `quedan` **dentro** del `with`, y los uso después para escribir el mensaje.
- **La pausa de 0,05 s sigue dentro.** Es la misma ventana de la fase 1, y la dejo para demostrar que, aunque haya hueco, ya no se cuela nadie. En la versión final se quita, porque no necesita protección y solo hace esperar a las demás cajas.

### Prueba: la misma carrera, ahora con Lock

Ejecuto otra vez `py prueba_carrera.py`, con los mismos 6 routers y las mismas 6 cajas que piden 2:

> **Pon aquí tu salida** de `py prueba_carrera.py` y borra este aviso. Debería salir algo como esto (el orden de las cajas puede cambiar, los números no):

```text
Hay 6 unidades de Router WiFi
6 cajas piden 2 cada una a la vez

[caja-1] PRUEBA-1: vendo 2 x Router WiFi -> quedan 4
[caja-2] PRUEBA-2: vendo 2 x Router WiFi -> quedan 2
[caja-3] PRUEBA-3: vendo 2 x Router WiFi -> quedan 0
[caja-4] PRUEBA-4: NO hay bastante Router WiFi (hay 0, pide 2)
[caja-5] PRUEBA-5: NO hay bastante Router WiFi (hay 0, pide 2)
[caja-6] PRUEBA-6: NO hay bastante Router WiFi (hay 0, pide 2)

Stock final de Router WiFi: 0
```

Ahora sale lo correcto: **3 ventas, 3 rechazos y stock final 0**. Momento a momento:

| Momento | Quién tiene el cerrojo | Qué hace | Stock |
|---|---|---|---|
| 1 | caja-1 (las otras 5 esperan en la puerta) | lee 6, vende 2 | 4 |
| 2 | caja-2 | lee 4, vende 2 | 2 |
| 3 | caja-3 | lee 2, vende 2 | 0 |
| 4 | caja-4 | lee 0: NO vende | 0 |
| 5 | caja-5 | lee 0: NO vende | 0 |
| 6 | caja-6 | lee 0: NO vende | 0 |

Cada caja lee el stock **después** de que la anterior haya descontado, porque no puede entrar hasta que la otra suelta el cerrojo.

> **Pon aquí cuántas veces lo has ejecutado** (por ejemplo: «Lo he ejecutado 3 veces y las 3 ha salido stock final 0»).

### `main.py` con Lock

El stock final sale igual que antes (39 ventas, y PED-040 rechazado porque pide 4 Router WiFi y quedan 3), pero ahora **tarda más**: unos 2 segundos, en vez de menos de medio. Cada venta tiene el cerrojo cogido 0,05 s y las ventas van de una en una: 40 × 0,05 s ≈ 2 s. Es el precio de sincronizar: se gana corrección pero se pierde concurrencia. Por eso la sección crítica tiene que ser lo más pequeña posible.

> **Pon aquí cuánto te tarda** y cuántas veces lo has ejecutado.

### Conclusión

Con el `Lock`, leer, comprobar y descontar se hacen como una sola operación y de una caja en una. El stock ya no puede quedar en valores incoherentes: nunca se venden unidades que no existen.

## Pruebas realizadas

| Prueba | Cómo la hago | Resultado |
|---|---|---|
| Mostrar una condición de carrera antes de sincronizar | `py prueba_carrera.py` con el código de la fase 1 (varias veces) | Las 6 cajas venden 2 routers cuando solo había 6, y el stock final es 4 en vez de 0. El fallo aparece. |
| Ejecutar la aplicación varias veces (fase 1) | `py main.py` (varias veces) | 39 ventas y 1 rechazo (PED-040). Con este reparto el fallo casi nunca se ve. |
| Comprobar que Lock corrige el acceso concurrente | `py prueba_carrera.py` con el código de la fase 2 (varias veces) | Siempre 3 ventas, 3 rechazos y stock final 0. |
| Ejecutar la aplicación varias veces (fase 2) | `py main.py` (varias veces) | Mismo stock final todas las veces; tarda unos 2 s por el cerrojo. |

## Ramas y commits

- `main`: versión estable (de momento, solo el inicio del proyecto).
- `develop`: rama de integración.
- `feature/race-condition`: fase 1, ya juntada con `develop`.
- `feature/lock-inventario`: fase 2, creada desde `develop` actualizado y juntada con `develop` al terminar.