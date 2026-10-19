# Documento final: Nodo, una mini red social

**Estudiante:** Juan Carlos Gallego Barona
**Materia:** Estructuras de Datos, Universidad Autónoma de Occidente
**Repositorio:** https://github.com/JGall3go/mini-red-social

---

## 1. ¿Qué es Nodo?

Nodo es una red social pequeña que hice para el proyecto final. La idea no era hacer un Facebook completo, sino una red sencilla donde cada función usa una estructura de datos que programé yo mismo, sin librerías como `networkx`, `deque` o `heapq`.

## 2. Alcance del sistema

Lo que **sí** hace el sistema:

- **Registrarse** solo con un nombre de usuario, un nombre visible y una biografía opcional. No hay contraseñas: en la página de inicio se elige con qué usuario entrar.
- **Buscar usuarios** con autocompletado: mientras se escribe aparecen los nombres que empiezan por esas letras.
- **Enviar solicitudes de amistad**, y **aceptarlas o rechazarlas** en el orden en que llegaron.
- Ver **sugerencias de amigos**, que son los amigos de mis amigos.
- Calcular los **grados de separación** entre dos usuarios, es decir, cuántos "saltos" de amistad hay entre ellos.
- **Publicar**, editar y borrar publicaciones.
- Dar y quitar **likes**.
- Ver un **feed** con mis publicaciones y las de mis amigos, ordenado por fecha o por likes.
- Ver el **grafo de amistades** dibujado e interactivo.
- Una página de **"Estructuras"** que muestra cómo están por dentro el Trie, el BST, la Cola y la Lista enlazada con los datos reales.

Lo que **no** hace (quedó fuera del alcance):

- Inicio de sesión con contraseña ni seguridad de cuentas.
- Fotos, comentarios ni mensajes privados.
- Notificaciones en tiempo real.

## 3. Tecnologías utilizadas

| Parte | Tecnología | Para qué la usé |
|---|---|---|
| Lenguaje del backend | Python 3.12 | Las estructuras de datos y la lógica |
| API | FastAPI + Uvicorn | Exponer las funciones como endpoints REST (`/usuarios`, `/solicitudes`, `/feed`, etc.) |
| Base de datos | PostgreSQL 16 | Guardar los datos de forma permanente |
| Conexión a la BD | SQLAlchemy | Crear las tablas, hacer el CRUD y manejar las transacciones |
| Frontend | HTML, CSS y JavaScript sin frameworks | Las páginas que ve el usuario |
| Dibujo del grafo y los árboles | vis-network | Mostrar el grafo de amistades, el Trie y el BST |
| Pruebas | pytest | 79 pruebas automáticas |
| Contenedores | Docker | Base de datos local y las imágenes para desplegar |
| Despliegue | Coolify (servidor de la empresa) | Publicar la base de datos, la API y la web |
| Control de versiones | Git y GitHub | Una rama por módulo, unida a `main` con merge |

### ¿Cómo funciona por dentro?

1. Cuando la API arranca, lee todo de PostgreSQL y lo carga en mis estructuras de datos en memoria.
2. Cuando alguien **consulta** algo (buscar, ver el feed, sugerencias), la respuesta sale de las estructuras, no de una consulta SQL.
3. Cuando alguien **cambia** algo (crear usuario, dar like, aceptar una solicitud), primero se guarda en PostgreSQL y después se actualiza la estructura.

Así los datos no se pierden si se reinicia el servidor, y la lógica la hacen las estructuras que programé.

### Transacciones

Algunas operaciones cambian varias tablas a la vez. Por eso se hacen dentro de una transacción: si algo falla, se hace *rollback* y no queda nada a medias.

- **Aceptar una solicitud:** se marca la solicitud como aceptada y se crea la amistad.
- **Dar like:** se guarda el like y se suma 1 al contador del post.
- **Quitar like:** se borra el like y se resta 1 al contador.
- **Eliminar un usuario:** primero se restan sus likes de los posts de otros y después se borran sus datos.

---

## 4. Estructuras de datos

Programé 5 estructuras desde cero. Están en `backend/app/estructuras/`, y cada una tiene sus pruebas en `backend/tests/`.

### 4.1 Lista enlazada (`lista_enlazada.py`)

**Cómo la hice:** es una cadena de nodos donde cada nodo guarda un valor y apunta al siguiente. Guardo una referencia al primero (`cabeza`) y al último (`cola`), y un contador del tamaño.

**Dónde la uso:**
- Las **publicaciones de cada usuario**. Cada post nuevo se inserta al inicio, así la lista siempre queda de la más nueva a la más vieja sin tener que ordenar.
- Los **amigos de cada usuario** dentro del grafo.
- Los **likes de cada usuario**: la lista de posts a los que les dio like, para que el botón muestre "Me gusta" o "Quitar like" correctamente.

**Por qué la escogí:** lo que más se hace con las publicaciones es agregar una nueva y recorrerlas en orden, y la lista enlazada hace las dos cosas bien. Además, para armar el feed por fecha uno las listas de varios amigos con el mismo paso de "mezcla" del merge sort, sin ordenar todo desde cero.

| Operación | Complejidad |
|---|---|
| Insertar al inicio | O(1) |
| Insertar al final | O(1), gracias a la referencia al último nodo |
| Buscar | O(n) |
| Eliminar | O(n) |
| Recorrer | O(n) |

### 4.2 Cola (`cola.py`)

**Cómo la hice:** también con nodos, pero solo se agrega por el final y solo se saca por el frente (FIFO: el primero que entra es el primero que sale).

**Dónde la uso:**
- Las **solicitudes de amistad pendientes** de cada usuario. Solo se puede aceptar o rechazar la más antigua, como una fila en el banco.
- El **BFS** del grafo, que necesita una cola para recorrer por niveles.

**Por qué la escogí:** las solicitudes deben responderse en el orden en que llegaron, y eso es justo lo que hace una cola. Si usara una lista de Python normal, sacar el primer elemento costaría O(n) porque se corren todos los demás. Con nodos cuesta O(1).

| Operación | Complejidad |
|---|---|
| Encolar | O(1) |
| Desencolar | O(1) |
| Ver el frente | O(1) |

### 4.3 Grafo con lista de adyacencia (`grafo.py`)

**Cómo lo hice:** es un diccionario donde cada usuario es una llave y su valor es una lista enlazada con sus amigos. Es un grafo **no dirigido**: si Ana es amiga de Beto, Beto también es amigo de Ana.

**Dónde lo uso:**
- Guardar todas las **amistades**.
- **Sugerencias de amigos:** con un BFS busco los usuarios que están a distancia 2 (amigos de mis amigos que todavía no son mis amigos) y los ordeno por cuántos amigos tenemos en común.
- **Grados de separación:** con un BFS busco el camino más corto entre dos usuarios. Los grados son el número de saltos del camino.
- El **feed**, para saber de quién mostrar publicaciones.

**Por qué lo escogí:** una red social *es* un grafo: personas conectadas con personas. Escogí lista de adyacencia y no matriz de adyacencia porque cada persona tiene pocos amigos comparado con el total de usuarios. Una matriz gastaría espacio V×V casi todo en ceros, y la lista solo guarda las amistades que existen.

Usé **BFS** y no DFS porque el BFS recorre por niveles (primero los amigos, luego los amigos de los amigos...). Por eso la primera vez que llega a una persona lo hace por el camino más corto.

| Operación | Complejidad (V = usuarios, E = amistades, g = amigos de un usuario) |
|---|---|
| Agregar usuario | O(1) |
| Agregar o quitar amistad | O(g) |
| ¿Son amigos? | O(g) |
| BFS, sugerencias, grados de separación | O(V + E) |

### 4.4 Trie o árbol de prefijos (`trie.py`)

**Cómo lo hice:** cada nodo representa una letra y tiene un diccionario con sus hijos. Las palabras que empiezan igual comparten el mismo camino desde la raíz: por ejemplo "juan" y "julia" comparten "j → u". Cada nodo tiene una marca `es_fin` que indica si ahí termina un nombre de usuario. Guardo todo en minúscula para que la búsqueda no distinga mayúsculas.

**Dónde lo uso:** en el **buscador con autocompletado**. Cuando el usuario escribe "ju", bajo por la "j" y la "u" y recojo todos los nombres que hay debajo.

**Por qué lo escogí:** para buscar por prefijo, recorrer la lista de todos los usuarios comparando el inicio de cada nombre cuesta O(n·m). Con el Trie solo bajo por las letras del prefijo, y el costo depende del largo de lo que se escribe, no de cuántos usuarios hay.

| Operación | Complejidad (m = largo de la palabra) |
|---|---|
| Insertar | O(m) |
| Buscar | O(m) |
| Eliminar | O(m) |
| Autocompletar | O(m + k), donde k son los nodos debajo del prefijo |

### 4.5 Árbol binario de búsqueda o BST (`bst.py`)

**Cómo lo hice:** cada nodo tiene una clave, un valor y dos hijos. Las claves menores van a la izquierda y las mayores a la derecha. La clave de cada publicación es `(likes, fecha, id)`: si dos posts tienen los mismos likes se desempata por fecha, y si también coinciden, por id. Así nunca hay claves repetidas.

**Dónde lo uso:** en el **feed ordenado por likes**. Recorro el árbol en **in-order inverso** (derecha, raíz, izquierda) y las publicaciones salen de la que tiene más likes a la que tiene menos. Cuando alguien da o quita un like, la clave del post cambia, así que lo saco del árbol y lo vuelvo a insertar con la clave nueva.

**Por qué lo escogí:** necesitaba tener las publicaciones siempre ordenadas por likes, aunque los likes cambian todo el tiempo. Con el BST no tengo que reordenar todo cada vez: basta con sacar e insertar un solo nodo.

**Limitación que encontré:** el BST no se balancea solo. Si las publicaciones llegan con las claves casi en orden, el árbol queda como una "escalera" (parecido a una lista) y las operaciones pasan de O(log n) a O(n). Se ve en la página de Estructuras y lo comprueba una de las pruebas (`test_bst.py`). Para mejorarlo se podría usar un árbol AVL o rojo-negro, que se balancean solos.

| Operación | Complejidad (h = altura del árbol) |
|---|---|
| Insertar | O(h) |
| Buscar | O(h) |
| Eliminar | O(h) |
| Recorrido in-order | O(n) |

h vale log n si el árbol está balanceado, pero puede llegar a n en el peor caso.

### Resumen

| Estructura | Función de la red social | Por qué |
|---|---|---|
| Lista enlazada | Publicaciones, amigos y likes de cada usuario | Insertar al inicio en O(1) y recorrer en orden |
| Cola | Solicitudes de amistad y BFS | Respeta el orden de llegada (FIFO) en O(1) |
| Grafo | Amistades, sugerencias y grados de separación | Una red social es un grafo, y BFS da el camino más corto |
| Trie | Búsqueda con autocompletado | Busca por prefijo en O(m) sin revisar a todos los usuarios |
| BST | Feed ordenado por likes | Mantiene el orden aunque los likes cambien |

---

## 5. Pruebas

Hay **79 pruebas** con pytest, que se corren con `python -m pytest` dentro de la carpeta `backend`:

| Archivo | Pruebas | Qué revisa |
|---|---|---|
| `test_lista_enlazada.py` | 13 | Insertar, buscar y eliminar al inicio, en el medio y al final |
| `test_cola.py` | 8 | Orden FIFO y error al sacar de una cola vacía |
| `test_trie.py` | 11 | Autocompletado, mayúsculas, eliminar sin dañar otras palabras |
| `test_bst.py` | 12 | Orden in-order, eliminar con dos hijos, el caso degenerado |
| `test_grafo.py` | 12 | BFS, sugerencias y grados de separación |
| `test_crud.py` | 11 | CRUD y que las transacciones hagan rollback si algo falla |
| `test_api.py` | 12 | Los endpoints de la API funcionando juntos |

## 6. Conclusiones

- Hacer las estructuras a mano me ayudó a entender por qué cada una sirve para algo distinto: no es lo mismo buscar por prefijo que mantener un orden o recorrer conexiones.
- La parte más interesante fue el grafo, porque con un solo BFS salen tanto las sugerencias como los grados de separación.
- El BST me mostró en la práctica que un árbol sin balancear puede volverse lento, algo que en clase había visto solo en teoría.
- Separar la base de datos (para guardar) de las estructuras (para la lógica) hizo que el código quedara más ordenado y fácil de probar.
