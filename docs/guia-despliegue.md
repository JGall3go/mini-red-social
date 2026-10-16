# Guía de despliegue en Coolify

Nodo se despliega en el Coolify del servidor de la empresa como **tres recursos** dentro de un mismo proyecto:

| Recurso | Qué es | Puerto interno |
|---|---|---|
| `nodo-db` | Base de datos PostgreSQL 16 | 5432 |
| `nodo-api` | Backend FastAPI (`backend/Dockerfile`) | 8000 |
| `nodo-web` | Frontend estático con nginx (`frontend/Dockerfile`) | 80 |

Coolify construye las dos imágenes a partir del repositorio de GitHub (rama `main`) y les pone HTTPS con Let's Encrypt.

## Antes de empezar

- Tener acceso al panel de Coolify y a un servidor ya agregado en él.
- Que Coolify tenga acceso al repositorio `mini-red-social` (con la GitHub App de Coolify, o con el repositorio público).
- Definir los dos dominios. En esta guía usamos de ejemplo:
  - API: `https://api-nodo.ejemplo.com`
  - Web: `https://nodo.ejemplo.com`

  Los dos deben apuntar (registro DNS tipo A) a la IP del servidor. Si no hay dominio propio, se pueden usar los dominios `sslip.io` que Coolify genera solo.

## 1. Crear la base de datos

1. En Coolify: **Projects → New Project**, con el nombre `Nodo`.
2. Dentro del proyecto: **+ New → Database → PostgreSQL** (versión 16).
3. Ponerle de nombre `nodo-db`. Coolify genera solo el usuario y la contraseña.
4. Pulsar **Start**.
5. Copiar la **Postgres URL (internal)**. Se ve así:
   `postgres://usuario:clave@nodo-db-xxxx:5432/postgres`

   No hace falta cambiar `postgres://`: `app/config.py` lo convierte a `postgresql+psycopg://`.

No marques "Make it publicly available": la base de datos solo la usa la API, por la red interna de Coolify.

## 2. Desplegar la API

1. **+ New → Application → (Private Repository con GitHub App | Public Repository)** y elegir el repo `mini-red-social`, rama `main`.
2. **Build Pack:** `Dockerfile`.
3. **Base Directory:** `/backend`.
4. **Ports Exposes:** `8000`.
5. **Domains:** `https://api-nodo.ejemplo.com`.
6. En **Environment Variables**:

   | Variable | Valor |
   |---|---|
   | `DATABASE_URL` | la URL interna copiada en el paso 1 |
   | `ORIGENES_PERMITIDOS` | `https://nodo.ejemplo.com` |

7. Opcional, en **Health Check**: ruta `/salud`, puerto `8000`.
8. **Deploy.**

Al arrancar, el contenedor ejecuta `python crear_tablas.py`, que crea las tablas si no existen, y luego levanta uvicorn con **un solo worker**. Debe ser uno solo porque las estructuras (grafo, trie, BST, colas y listas) viven en la memoria del proceso. Con varios workers, cada uno tendría su propia copia y se desincronizarían.

**Comprobar:** abrir `https://api-nodo.ejemplo.com/salud`, que debe responder `{"estado":"ok"}`, y `https://api-nodo.ejemplo.com/docs`.

## 3. Desplegar el frontend

1. **+ New → Application**, el mismo repositorio y la rama `main`.
2. **Build Pack:** `Dockerfile`.
3. **Base Directory:** `/frontend`.
4. **Ports Exposes:** `80`.
5. **Domains:** `https://nodo.ejemplo.com`.
6. En **Environment Variables**:

   | Variable | Valor |
   |---|---|
   | `API_URL` | `https://api-nodo.ejemplo.com` (sin `/` al final) |

7. **Deploy.**

Al arrancar el contenedor, el script `frontend/docker/generar-config.sh` reescribe `js/config.js` con el valor de `API_URL`. Así no hay que editar el código para cambiar la dirección de la API. En local, `config.js` sigue apuntando a `http://localhost:8000`.

**Comprobar:** abrir `https://nodo.ejemplo.com/js/config.js`, que debe mostrar la URL pública de la API. Luego abrir `https://nodo.ejemplo.com`, crear un usuario y buscarlo con el autocompletado.

## 4. Prueba final

- [ ] `/salud` de la API responde por HTTPS.
- [ ] La página de inicio carga la lista de usuarios, sin el error "No se pudo conectar con la API".
- [ ] Crear dos usuarios, enviar y aceptar una solicitud de amistad.
- [ ] Publicar y dar like. Ver el feed por fecha y por likes.
- [ ] Ver el grafo y los grados de separación.
- [ ] Reiniciar la API desde Coolify (**Restart**) y comprobar que los datos siguen ahí, porque se recargan desde PostgreSQL.
- [ ] Probar desde el celular con datos móviles, para confirmar que se ve fuera de la red de la empresa.

## Problemas comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| En el navegador sale un error de **CORS** | `ORIGENES_PERMITIDOS` no coincide exactamente con el dominio del frontend | Poner el dominio con `https://` y sin `/` final, y hacer Redeploy de la API |
| "No se pudo conectar con la API" | `API_URL` mal escrita o la API caída | Revisar `/js/config.js` y los logs de `nodo-api` |
| La API se reinicia en bucle | `DATABASE_URL` incorrecta o la BD apagada | Revisar que `nodo-db` esté en *Running* y usar la URL **interna** |
| *Mixed content* en la consola | `API_URL` usa `http://` pero la web está en `https://` | Usar `https://` en `API_URL` |
| El grafo no se dibuja | El navegador no pudo cargar vis-network desde unpkg | Revisar la conexión a internet o si un firewall bloquea `unpkg.com` |

## Actualizar la aplicación

Cada vez que se hace merge a `main` y se sube con `git push`, se pulsa **Redeploy** en `nodo-api` y en `nodo-web`. También se puede activar **Auto Deploy** en cada recurso para que Coolify lo haga solo con cada push.

## Probar las imágenes en local (opcional)

Desde la raíz del proyecto, con Docker Desktop abierto:

```bash
docker build -t nodo-api backend
docker build -t nodo-web frontend
docker run --rm -p 8080:80 -e API_URL=http://localhost:8000 nodo-web
```

Esto sirve el frontend en http://localhost:8080 usando la API que ya tengas corriendo en el puerto 8000.
