# StockFlow
 
## Descripción
 
StockFlow simula una tienda en la que varias **cajas** venden pedidos **a la vez** sobre un **mismo inventario**. Cada caja es un hilo (`threading.Thread`). Como todas las cajas leen y cambian el mismo stock, pueden aparecer problemas de concurrencia.
 
El proyecto se hace por fases: primero se programa **sin sincronización**, para ver el fallo, y después se va corrigiendo con `Lock`, `Semaphore`, `Condition`, `Barrier` y `RLock`.
 
> Estado actual: **Fase 6** (el inventario es una clase, `GestorInventario`, protegida con `RLock`; terminales con `Semaphore`, reposición con `Condition` y revisión final con `Barrier`).
 
## Cómo ejecutarlo
 
Necesitas Python 3 (yo uso Python 3.14 en Windows). Desde la carpeta del proyecto:
 
```powershell
py main.py              # ventas y reposiciones; al final, 4 revisores revisan el inventario
py prueba_carrera.py    # 6 cajas compiten a la vez por el mismo producto
```
 
## Estructura de archivos
 
```text
stockflow/
├── datos.py             # datos de partida del profesor (no se modifica)
├── inventario.py        # la clase GestorInventario: stock, RLock, Condition y sus métodos
├── hilos.py             # las clases Caja, Almacen y Revisor (hilos que reciben el gestor)
├── main.py              # crea el gestor; lanza cajas y almacén; después, los 4 revisores
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
 
## Fase 3 · Terminales limitados con Semaphore
 
### El problema
 
Hay **6 cajas** pero solo **3 terminales de cobro** (`NUM_TERMINALES = 3` en `datos.py`). Como mucho 3 cajas pueden estar cobrando a la vez; las demás tienen que esperar a que se quede un terminal libre.
 
### Qué he cambiado
 
En `main.py` creo **un** semáforo y se lo paso a las 6 cajas:
 
```python
terminales = threading.Semaphore(NUM_TERMINALES)   # 3 plazas
 
cajas.append(Caja(f"caja-{i + 1}", mis_pedidos, terminales))
```
 
En `hilos.py`, la caja guarda el semáforo y lo usa al procesar cada pedido:
 
```python
def run(self):
    for numero_pedido, producto, unidades in self.pedidos:
        print(f"[{self.name}] espero terminal para {numero_pedido}")
        with self.terminales:                      # coge un terminal (o espera)
            print(f"[{self.name}] COJO terminal")
            vender(self.name, numero_pedido, producto, unidades)
            time.sleep(0.1)                        # cobrar
            print(f"[{self.name}] SUELTO terminal")
                                                   # aquí lo suelta
```
 
`inventario.py` no cambia: el `Lock` sigue ahí.
 
### Para qué sirve el Semaphore
 
Un `Semaphore(3)` es un **aforo de 3**: es como tener 3 llaves en vez de una. Cada caja que entra en `with self.terminales:` coge una plaza; si las 3 están ocupadas, la caja espera ahí hasta que otra salga y deje su plaza libre.
 
Los mensajes «espero terminal», «COJO terminal» y «SUELTO terminal» sirven para **ver en la salida** cuándo una caja pide, obtiene y libera un terminal, como pide el enunciado.
 
### Semaphore y Lock resuelven problemas distintos
 
| | `Semaphore(3)` | `Lock` |
|---|---|---|
| Qué protege | los terminales de cobro | el inventario |
| Cuántas cajas dentro a la vez | hasta 3 | solo 1 |
| Pregunta que responde | ¿cuántas cajas pueden cobrar a la vez? | ¿quién puede tocar el stock ahora? |
 
El semáforo **no** sirve para proteger el inventario: dentro de él puede haber 3 cajas a la vez, y esas 3 podrían leer y descontar el mismo producto a la vez (la carrera de la fase 1). Por eso se mantiene el `Lock` en `vender()`: cada mecanismo resuelve su propio problema.
 
### Decisiones importantes
 
- **Un solo semáforo, creado en `main.py`.** Se crea antes que las cajas y se le pasa el **mismo** objeto a las 6. Si cada caja creara su propio `Semaphore(3)`, cada una tendría 3 terminales para ella sola y no habría ningún límite.
- **Uso `NUM_TERMINALES`, no el número 3 a mano.** Si cambian los datos, el programa sigue funcionando sin tocar el código.
- **El orden es siempre el mismo:** primero el terminal (`with self.terminales:`) y después, dentro de `vender()`, el cerrojo del inventario. Ninguna parte del programa coge el cerrojo y luego un terminal. Esto es importante para evitar bloqueos (lo analizo en la fase 7).
- **Cobrar (`time.sleep(0.1)`) se hace con el terminal, pero fuera del Lock.** Cobrar no toca el inventario, así que mientras una caja cobra, otra puede estar usando el inventario.
### Prueba: más cajas que terminales
 
Ejecuto `py main.py`:
 
> **Pon aquí un trozo de tu salida** donde se vean «espero terminal», «COJO» y «SUELTO», y borra este aviso. Debería salir algo como esto:
 
```text
[caja-1] espero terminal para PED-001
[caja-1] COJO terminal
[caja-2] espero terminal para PED-002
[caja-2] COJO terminal
[caja-3] espero terminal para PED-003
[caja-3] COJO terminal
[caja-4] espero terminal para PED-004
[caja-5] espero terminal para PED-005
[caja-6] espero terminal para PED-006
[caja-1] PED-001: vendo 4 x Teclado mecanico -> quedan 14
[caja-2] PED-002: vendo 5 x Raton gaming -> quedan 15
[caja-3] PED-003: vendo 3 x Monitor 24 pulgadas -> quedan 7
[caja-1] SUELTO terminal
[caja-1] espero terminal para PED-007
[caja-1] COJO terminal
...
```
 
Las 6 cajas piden terminal a la vez, pero solo caja-1, caja-2 y caja-3 lo cogen. caja-4, caja-5 y caja-6 se quedan esperando. Contando los «COJO» y los «SUELTO» de toda la salida, **nunca hay más de 3 cajas con terminal a la vez**.
 
Una cosa curiosa que he visto: caja-1, caja-2 y caja-3 hacen **todos** sus pedidos antes de que entren las otras tres. La caja que suelta el terminal lo vuelve a pedir enseguida y lo consigue antes que las que llevaban rato esperando. El `Semaphore` limita cuántas entran, pero **no garantiza el orden de llegada**.
 
> **Pon aquí cuántas veces lo has ejecutado y cuánto tarda** (a mí, unos 2 segundos).
 
### Conclusión
 
Con el `Semaphore`, como mucho 3 cajas cobran a la vez, y las demás esperan sin hacer nada hasta que se libera un terminal. El `Lock` sigue protegiendo el inventario, así que el stock final sigue saliendo bien.
 
## Fase 4 · Reposición con Condition
 
### El problema
 
Hasta ahora, si no había stock suficiente, la venta se rechazaba (como PED-040). Ahora hay un **almacén** que va reponiendo mercancía (`REPOSICIONES` de `datos.py`). Si una caja no tiene stock suficiente, **no rechaza el pedido: espera** a que el almacén reponga.
 
El enunciado prohíbe hacerlo con **espera activa**, es decir, con un bucle que pregunte todo el rato «¿ya hay?»:
 
```python
while inventario[producto] < unidades:
    pass        # MAL: gasta CPU sin hacer nada útil
```
 
### Qué he cambiado
 
En `inventario.py` creo una `Condition` que usa **el mismo** `Lock` del inventario, y cambio `vender()`:
 
```python
lock = threading.Lock()
condicion = threading.Condition(lock)     # la sala de espera, con el MISMO cerrojo
 
def vender(caja, numero_pedido, producto, unidades, esperar=True):
    with condicion:                                        # coge el cerrojo
        while inventario[producto] < unidades and esperar: # ¿me llega?
            print(f"[{caja}] {numero_pedido}: espero reposición de ...")
            condicion.wait()                               # suelta el cerrojo y duerme
        # ... a partir de aquí, igual que en la fase 2 (comprobar y descontar)
```
 
Y añado `reponer()`, que es lo que usa el almacén:
 
```python
def reponer(quien, numero_albaran, producto, unidades):
    with condicion:                        # coge el cerrojo
        inventario[producto] += unidades
        hay = inventario[producto]
        condicion.notify_all()             # despierta a TODAS las cajas que esperan
    print(f"[{quien}] {numero_albaran}: repongo ...")   # el print, fuera
```
 
En `hilos.py` hay una clase nueva, `Almacen`, que también es un hilo:
 
```python
class Almacen(threading.Thread):
    def __init__(self, reposiciones):
        super().__init__(name="almacen")
        self.reposiciones = list(reposiciones)
 
    def run(self):
        time.sleep(1.5)                    # el camión tarda en llegar
        for numero_albaran, producto, unidades in self.reposiciones:
            reponer(self.name, numero_albaran, producto, unidades)
            time.sleep(0.3)                # un albarán cada 0,3 s
```
 
En `main.py` creo el almacén, lo lanzo a la vez que las cajas (`start()`) y lo espero al final con las cajas (`join()`).
 
### Para qué sirve la Condition
 
Una `Condition` es como una **sala de espera con un timbre**:
 
- `wait()`: la caja **suelta el cerrojo** del inventario y **se duerme**, sin gastar CPU. Cuando la despiertan, vuelve a coger el cerrojo antes de seguir.
- `notify_all()`: el almacén **toca el timbre** y despierta a **todas** las cajas que están durmiendo.
Hay dos esperas diferentes y no hay que confundirlas:
 
| | Esperar el cerrojo | Esperar en `wait()` |
|---|---|---|
| Por qué espera | otra caja está dentro con el cerrojo | falta stock |
| Qué la despierta | que la otra salga y suelte el cerrojo | que alguien haga `notify_all()` |
| Tiene el cerrojo mientras espera | no | no (`wait()` lo suelta) |
 
### Decisiones importantes
 
- **La `Condition` usa el mismo `Lock` del inventario** (`Condition(lock)`). Así hay un solo cerrojo protegiendo el stock. Si la `Condition` tuviera otro cerrojo distinto, habría dos cerrojos protegiendo lo mismo y volvería a haber carreras.
- **`wait()` suelta el cerrojo mientras duerme.** Si la caja se durmiera con el cerrojo cogido, el almacén nunca podría entrar a reponer y la caja no despertaría nunca.
- **Uso `while` y no `if`.** Al despertarse, la caja **vuelve a comprobar** si ya tiene stock. Puede que la hayan despertado por una reposición de otro producto, o que otra caja se le haya adelantado. Con un `if` vendería sin volver a mirar. Lo he visto en la prueba: caja-4 se despierta 2 veces sin que haya routers suficientes y se vuelve a dormir (lo explico abajo).
- **Uso `notify_all()` y no `notify()`.** Puede haber varias cajas esperando productos **distintos**. `notify()` despierta solo a una, y podría ser una que espera otro producto: la que necesita lo que ha llegado seguiría durmiendo. Con `notify_all()` se despiertan todas, y cada una mira su `while`: la que ya tiene stock vende y las demás se vuelven a dormir.
- **El almacén espera 1,5 s antes de empezar.** Así alguna caja **tiene** que esperar una reposición, que es una de las pruebas obligatorias.
- **El almacén no usa terminal.** Reponer no es cobrar. Esto es importante: la caja que espera en `wait()` sigue teniendo su terminal, y si el almacén necesitara uno podría quedarse sin ninguno (lo analizo en la fase 7).
- **Parámetro `esperar=True`.** Por defecto, la caja espera. En `prueba_carrera.py` no hay almacén, así que si las cajas esperaran se quedarían dormidas para siempre. Por eso allí llamo a `vender(..., False)`: sin stock, se rechaza como antes.
### Prueba: una venta que espera y una reposición que la despierta
 
Ejecuto `py main.py`. El pedido que tiene que esperar es **PED-040** (caja-4): pide **4 Router WiFi** y solo quedan **3**, porque PED-025 ya vendió 3 de los 6.
 
> **Pon aquí el trozo de tu salida** con PED-040 y el almacén, y borra este aviso. Debería salir algo como esto:
 
```text
[caja-4] PED-040: espero reposición de Router WiFi (hay 3, pide 4)
[almacen] ALB-003: repongo 10 x SSD 1 TB -> hay 13
[caja-4] PED-040: espero reposición de Router WiFi (hay 3, pide 4)
[almacen] ALB-004: repongo 6 x Disco externo 2 TB -> hay 6
[caja-4] PED-040: espero reposición de Router WiFi (hay 3, pide 4)
[almacen] ALB-005: repongo 5 x Router WiFi -> hay 8
[caja-4] PED-040: vendo 4 x Router WiFi -> quedan 4
[caja-4] SUELTO terminal
```
 
Así pasa, momento a momento:
 
| Momento | almacén | caja-4 (PED-040) | Router WiFi |
|---|---|---|---|
| 1 | | llega a PED-040: hay 3, pide 4 → `wait()`, se duerme | 3 |
| 2 | ALB-003 (SSD) → `notify_all()` | despierta, mira el `while`: siguen 3 → se vuelve a dormir | 3 |
| 3 | ALB-004 (Disco) → `notify_all()` | despierta, siguen 3 → se vuelve a dormir | 3 |
| 4 | ALB-005 (+5 Router WiFi) → `notify_all()` | despierta, hay 8 ≥ 4 → sale del `while` y vende 4 | 8 → 4 |
 
«espero reposición» sale **3 veces**: cada albarán hace `notify_all()` y despierta a caja-4, pero solo con ALB-005 hay routers suficientes. **Esto demuestra por qué hace falta el `while`**: con un `if`, caja-4 habría vendido 4 routers teniendo solo 3.
 
Con la reposición, ya no se rechaza ningún pedido: **40 ventas y 0 rechazos**, y el stock final sale igual en todas las ejecuciones. Tarda unos 5 segundos, porque el almacén tarda 1,5 s en empezar y reparte un albarán cada 0,3 s.
 
> **Pon aquí cuántas veces lo has ejecutado y cuánto tarda.**
 
También he comprobado que `py prueba_carrera.py` (ahora con `esperar=False`) sigue saliendo bien: 3 ventas, 3 rechazos y stock final 0.
 
> **Pon aquí tu salida de `py prueba_carrera.py`**, o di que sale igual que en la fase 2.
 
### Conclusión
 
Con la `Condition`, una caja sin stock espera **dormida** (sin espera activa) y suelta el cerrojo mientras tanto. El almacén repone y avisa con `notify_all()`, y cada caja que despierta vuelve a comprobar su stock con el `while` antes de vender.
 
## Fase 5 · Revisión final con Barrier
 
### El problema
 
Cuando terminan las ventas y las reposiciones, **4 revisores** (`NUM_REVISORES = 4`) se reparten los 25 productos del catálogo y comprueban el stock de cada uno. El cierre no se puede dar por bueno hasta que **los 4** hayan terminado su parte, y el resumen final solo se muestra **después**.
 
### Qué he cambiado
 
En `inventario.py` añado una función para **leer** el stock de un producto con el cerrojo:
 
```python
def consultar(producto):
    with lock:                       # hasta para leer, con el cerrojo
        return inventario[producto]
```
 
En `hilos.py` hay una clase nueva, `Revisor`:
 
```python
class Revisor(threading.Thread):
    def __init__(self, nombre, productos, barrera):
        super().__init__(name=nombre)
        self.productos = list(productos)    # SU parte del catálogo
        self.barrera = barrera              # LA barrera, la misma para los 4
 
    def run(self):
        for producto in self.productos:
            print(f"[{self.name}] {producto}: {consultar(producto)}")
            time.sleep(0.1)
        print(f"[{self.name}] he terminado mi parte -> espero en la barrera")
        self.barrera.wait()                 # espera aquí hasta que lleguen los 4
        print(f"[{self.name}] barrera superada")
```
 
En `main.py`, **después** de los `join()` de las cajas y del almacén:
 
```python
print("\n--- REVISIÓN FINAL ---")
productos = list(inventario)                     # los 25 nombres de producto
barrera = threading.Barrier(NUM_REVISORES)       # UNA barrera para los 4
 
revisores = []
for i in range(NUM_REVISORES):
    mis_productos = productos[i::NUM_REVISORES]  # uno de cada 4
    revisores.append(Revisor(f"revisor-{i + 1}", mis_productos, barrera))
 
for revisor in revisores:
    revisor.start()
for revisor in revisores:
    revisor.join()
 
print("\nSTOCK FINAL")                           # después de la barrera
```
 
### Para qué sirve la Barrier
 
Una `Barrier(4)` es como el **autobús de una excursión**: no sale hasta que han subido los 4. Cada revisor, al terminar su parte, llama a `barrera.wait()` y se queda ahí parado. Cuando llega el cuarto, la barrera se abre y **siguen los 4 a la vez**.
 
No hay que confundirla con el `Semaphore`:
 
| | `Semaphore(3)` | `Barrier(4)` |
|---|---|---|
| Pregunta que responde | ¿**cuántos** pueden entrar a la vez? | ¿**cuándo** puede seguir el grupo? |
| En StockFlow | como mucho 3 cajas cobrando | los 4 revisores esperan a que todos acaben |
 
### Decisiones importantes
 
- **El reparto del catálogo.** `list(inventario)` da solo los **nombres** de los productos, sin los números. Lo convierto en lista porque un diccionario no se puede trocear con `[i::4]`. Cada revisor se lleva uno de cada cuatro, como con los pedidos: revisor-1 se queda con 7 productos y los otros tres con 6 cada uno (25 = 7 + 6 + 6 + 6).
- **El revisor pregunta el número en el momento** con `consultar(producto)`. Así mira el inventario real, con el cerrojo, en vez de una copia hecha antes.
- **`consultar()` también coge el cerrojo**, aunque solo lea. Es el recurso compartido y nadie debería leerlo a medias mientras otro escribe.
- **`Barrier(NUM_REVISORES)`, exactamente 4.** Si pusiera `Barrier(5)` con 4 revisores, los 4 esperarían para siempre a un quinto que nunca llega, y el programa se quedaría colgado.
- **Una sola barrera**, creada en `main.py` y pasada a los 4 revisores. Si cada uno tuviera la suya, nadie esperaría a nadie.
- **`barrera.wait()` va fuera de cualquier cerrojo.** Si un revisor esperara en la barrera con el cerrojo del inventario cogido, los demás no podrían hacer `consultar()`, nunca llegarían a la barrera y se quedarían todos atascados (lo analizo en la fase 7).
- **La revisión empieza cuando ya han terminado las ventas**, porque `main` hace antes los `join()` de las cajas y del almacén.
- **`join()` y `Barrier` no son lo mismo.** Con `join()`, `main` espera a que un hilo **termine del todo**. Con la `Barrier`, los hilos se esperan **entre ellos** en un punto del medio de su trabajo y, cuando llegan todos, **siguen** («barrera superada»).
### Prueba: los revisores esperan en la Barrier
 
Ejecuto `py main.py`:
 
> **Pon aquí el trozo de tu salida** desde «--- REVISIÓN FINAL ---» hasta «STOCK FINAL», y borra este aviso. Debería salir algo como esto:
 
```text
--- REVISIÓN FINAL ---
[revisor-1] Teclado mecanico: 13
[revisor-2] Teclado inalambrico: 7
[revisor-3] Raton gaming: 18
[revisor-4] Raton oficina: 7
...
[revisor-3] he terminado mi parte -> espero en la barrera
[revisor-2] he terminado mi parte -> espero en la barrera
[revisor-4] he terminado mi parte -> espero en la barrera
[revisor-1] he terminado mi parte -> espero en la barrera
[revisor-1] barrera superada
[revisor-3] barrera superada
[revisor-2] barrera superada
[revisor-4] barrera superada
 
STOCK FINAL
...
```
 
Así pasa, momento a momento (a 0,1 s por producto):
 
| Momento | revisor-1 (7 productos) | revisores 2, 3 y 4 (6 productos) |
|---|---|---|
| 0,6 s | todavía revisando su último producto | terminan → `wait()`: esperan en la barrera |
| 0,7 s | termina → `wait()`: es el cuarto en llegar | — |
| justo después | la barrera se abre: los 4 siguen a la vez | |
 
Lo que demuestra que la barrera funciona: **los 4 «espero en la barrera» salen antes que cualquier «barrera superada»**. revisor-1 llega el último porque tiene un producto más, y los otros 3 le esperan. Después de los 4 «barrera superada» sale el «STOCK FINAL».
 
> **Pon aquí cuántas veces lo has ejecutado** y si siempre sale en ese orden (el orden de los revisores puede cambiar, pero nunca puede salir un «superada» antes del cuarto «espero»).
 
### Conclusión
 
Con la `Barrier`, ningún revisor da su parte por cerrada hasta que han terminado los 4, y el resumen final sale solo después de superar la barrera.
 
## Fase 6 · Refactorización con RLock
 
### El problema
 
Hasta ahora el inventario eran variables y funciones sueltas en `inventario.py` (`inventario`, `lock`, `condicion`, `vender()`…). El enunciado pide:
 
1. **Organizar el inventario en una clase.**
2. Que haya **al menos una operación protegida que llame a otra operación protegida** del mismo gestor.
3. Usar **`RLock`** para que eso funcione, y explicar por qué.
### Qué he cambiado
 
Todo lo del inventario está ahora dentro de la clase `GestorInventario`, en `inventario.py`:
 
```python
class GestorInventario:
    def __init__(self, stock_inicial):
        self._stock = dict(stock_inicial)
        self._lock = threading.RLock()                  # antes era Lock
        self._condicion = threading.Condition(self._lock)
 
    def consultar(self, producto): ...    # con self._lock
    def vender(self, caja, numero_pedido, producto, unidades, esperar=True): ...
    def reponer(self, quien, numero_albaran, producto, unidades): ...
    def productos(self): ...              # la lista de nombres, para los revisores
    def resumen(self): ...                # la foto final del inventario
```
 
El código de `vender()` y `reponer()` es **el mismo** que en la fase 4; solo cambian los nombres:
 
| Antes (fases 1 a 5) | Ahora (dentro de la clase) |
|---|---|
| `inventario = dict(STOCK_INICIAL)` | `self._stock = dict(stock_inicial)` |
| `lock = threading.Lock()` | `self._lock = threading.RLock()` |
| `condicion = threading.Condition(lock)` | `self._condicion = threading.Condition(self._lock)` |
| `def vender(caja, ...)` | `def vender(self, caja, ...)` |
| `vender(...)` desde `hilos.py` | `self.gestor.vender(...)` |
 
En `main.py` creo **un solo** gestor y se lo paso a todos los hilos:
 
```python
gestor = GestorInventario(STOCK_INICIAL)
 
Caja(f"caja-{i + 1}", mis_pedidos, terminales, gestor)
Almacen(REPOSICIONES, gestor)
Revisor(f"revisor-{i + 1}", mis_productos, barrera, gestor)
```
 
Las clases de `hilos.py` guardan el gestor en `self.gestor` y usan sus métodos (`self.gestor.vender(...)`, `self.gestor.reponer(...)`, `self.gestor.consultar(...)`). Ya no importan nada de `inventario.py`. `prueba_carrera.py` crea su propio gestor y usa `target=gestor.vender`.
 
### La operación protegida que llama a otra protegida
 
```python
def resumen(self):
    with self._lock:                                    # 1. coge el cerrojo
        copia = {}
        for producto in self._stock:
            copia[producto] = self.consultar(producto)  # 2. llama a otro método...
        return copia
 
def consultar(self, producto):
    with self._lock:                                    # 3. ...que coge el MISMO cerrojo
        return self._stock[producto]
```
 
`resumen()` coge el cerrojo para hacer una **foto completa** del inventario, de una vez, sin que nadie cambie nada en medio. Dentro llama a `consultar()`, que también coge el cerrojo. Es **el mismo hilo** cogiendo **el mismo cerrojo** dos veces.
 
### Por qué hace falta RLock
 
- **Con `Lock`:** el hilo coge el cerrojo en `resumen()` y, sin haberlo soltado, lo vuelve a pedir en `consultar()`. Como el cerrojo está cogido, se queda esperando a que lo suelten… pero quien lo tiene es **él mismo**. Se espera a sí mismo para siempre, sin dar ningún error.
- **Con `RLock`** (*Reentrant Lock*, cerrojo reentrante): el cerrojo recuerda **qué hilo** lo tiene y lleva un **contador**. Si el mismo hilo lo vuelve a pedir, le deja entrar y suma 1. Cada vez que sale de un `with`, resta 1. Cuando el contador vuelve a 0, queda libre para los demás hilos. Los **otros** hilos siguen esperando igual que con un `Lock`.
La `Condition` funciona igual con el `RLock`: `wait()` lo suelta mientras la caja duerme y lo recupera al despertar.
 
No uso `RLock` «por si acaso». Hasta la fase 5 bastaba con `Lock`. Lo cambio ahora porque `resumen()` llama a `consultar()` y sin reentrada se bloquearía.
 
### Decisiones importantes
 
- **Por qué una clase:** todo lo del inventario (el stock, su cerrojo, su `Condition` y sus operaciones) está junto en un solo objeto. Desde fuera solo se usan los métodos, y nadie toca el diccionario directamente.
- **El guion bajo delante** (`_stock`, `_lock`, `_condicion`) significa «de uso interno, no lo toques desde fuera de la clase».
- **Un solo gestor para todos los hilos.** Si cada caja creara su propio `GestorInventario`, cada una tendría su propio inventario y su propio cerrojo, y no compartirían nada.
- **`stock_inicial` se pasa al crear el gestor** en vez de importarlo dentro de la clase. Así `prueba_carrera.py` puede crear otro gestor distinto para su prueba.
### Prueba: Lock frente a RLock
 
Para comprobar que el `RLock` hace falta de verdad, he puesto **a propósito** `threading.Lock()` en el `__init__` y he ejecutado `py main.py`:
 
> **Pon aquí el final de tu salida con `Lock`**, y borra este aviso. Debería salir algo como esto:
 
```text
[revisor-4] barrera superada
 
STOCK FINAL
```
 
Se queda ahí, **colgado**: `resumen()` coge el cerrojo, llama a `consultar()`, este lo vuelve a pedir y el hilo se espera a sí mismo. He tenido que salir con **Ctrl+C**.
 
Después he vuelto a poner `threading.RLock()`:
 
> **Pon aquí el final de tu salida con `RLock`**, y borra este aviso. Debería salir algo como esto:
 
```text
STOCK FINAL
  Teclado mecanico: 13
  Teclado inalambrico: 7
  ...
  Toner negro: 14
```
 
Termina y muestra el stock final. También he comprobado que la versión con clase sigue haciendo lo mismo que antes: 40 ventas, 0 rechazos, el mismo stock final en todas las ejecuciones, y `py prueba_carrera.py` sigue dando 3 ventas, 3 rechazos y stock 0.
 
> **Pon aquí cuántas veces lo has ejecutado.**
 
### Conclusión
 
El inventario es ahora un objeto `GestorInventario` que guarda su stock y su cerrojo. `resumen()` es una operación protegida que llama a otra operación protegida, `consultar()`, del mismo gestor y desde el mismo hilo. Con un `Lock` normal eso se bloquea; con un `RLock` funciona, porque el mismo hilo puede volver a coger el cerrojo que ya tiene.
 
## Pruebas realizadas
 
| Prueba | Cómo la hago | Resultado |
|---|---|---|
| Mostrar una condición de carrera antes de sincronizar | `py prueba_carrera.py` con el código de la fase 1 (varias veces) | Las 6 cajas venden 2 routers cuando solo había 6, y el stock final es 4 en vez de 0. El fallo aparece. |
| Ejecutar la aplicación varias veces (fase 1) | `py main.py` (varias veces) | 39 ventas y 1 rechazo (PED-040). Con este reparto el fallo casi nunca se ve. |
| Comprobar que Lock corrige el acceso concurrente | `py prueba_carrera.py` con el código de la fase 2 (varias veces) | Siempre 3 ventas, 3 rechazos y stock final 0. |
| Ejecutar la aplicación varias veces (fase 2) | `py main.py` (varias veces) | Mismo stock final todas las veces; tarda unos 2 s por el cerrojo. |
| Tener más cajas que terminales disponibles | `py main.py` con 6 cajas y 3 terminales (fase 3) | Nunca hay más de 3 «COJO terminal» sin su «SUELTO». Las demás cajas esperan. |
| Provocar una venta que tenga que esperar a una reposición | `py main.py` (fase 4) | PED-040 pide 4 Router WiFi y hay 3: escribe «espero reposición» y se duerme en `wait()`. |
| Comprobar que una reposición permite continuar a una caja en espera | `py main.py` (fase 4) | Cuando llega ALB-005 (+5 Router WiFi, hay 8), caja-4 despierta y vende 4. Quedan 4. |
| Ejecutar la aplicación varias veces (fase 4) | `py main.py` (varias veces) | 40 ventas, 0 rechazos y el mismo stock final todas las veces. |
| La prueba de la carrera sigue bien | `py prueba_carrera.py` con `esperar=False` (fase 4) | Sigue saliendo 3 ventas, 3 rechazos y stock final 0. |
| Comprobar que los revisores esperan en la Barrier | `py main.py` (fase 5) | Los 4 «espero en la barrera» salen antes que cualquier «barrera superada». revisor-1 llega el último y los otros 3 le esperan. |
| Mostrar el resumen solo después de la barrera | `py main.py` (fase 5) | «STOCK FINAL» sale siempre después de los 4 «barrera superada». |
| Operación protegida que llama a otra protegida, con `Lock` | `py main.py` poniendo `threading.Lock()` en el gestor (fase 6) | Escribe «STOCK FINAL» y se queda colgado: `resumen()` llama a `consultar()` y el hilo se espera a sí mismo. |
| La misma operación con `RLock` | `py main.py` con `threading.RLock()` (fase 6) | Termina y muestra el stock final. |
| Ejecutar varias veces la versión con clase | `py main.py` y `py prueba_carrera.py` (fase 6) | 40 ventas, 0 rechazos y el mismo stock final; la prueba sigue saliendo 3 ventas, 3 rechazos y stock 0. |
 
## Ramas y commits
 
- `main`: versión estable (de momento, solo el inicio del proyecto).
- `develop`: rama de integración.
- `feature/race-condition`: fase 1, ya juntada con `develop`.
- `feature/lock-inventario`: fase 2, ya juntada con `develop`.
- `feature/semaphore-terminales`: fase 3, ya juntada con `develop`.
- `feature/condition-reposicion`: fase 4, ya juntada con `develop`.
- `feature/barrier-inventario`: fase 5, ya juntada con `develop`.
- `feature/rlock-gestor`: fase 6, creada desde `develop` actualizado y juntada con `develop` al terminar.