# Ledger — seguimiento diario de tu fondo Fidelity

## Qué es esto
Una PWA (app web instalable) que muestra el valor liquidativo diario de tu
fondo indexado, sin backend propio: GitHub descarga el precio por ti una vez
al día y tu móvil solo lee ese archivo.

## Puesta en marcha (una sola vez)

1. Crea un repo **público** en GitHub y sube TODO el contenido de esta
   carpeta (incluida la carpeta oculta `.github/`, no la olvides).

2. **Paso crítico que mucha gente se salta:** ve a
   `Settings → Actions → General → Workflow permissions` en tu repo,
   y marca **"Read and write permissions"**. Sin esto, la automatización
   descarga los precios pero no puede guardarlos (falla el `git push`).

3. Ve a la pestaña **Actions** de tu repo → click en "Actualizar precios"
   (el workflow) → botón **"Run workflow"** → Run. Espera ~30 segundos:
   esto genera los primeros datos (si no lo haces, la app se queda vacía
   hasta la próxima ejecución programada, esa tarde).

4. Ve a `Settings → Pages` → Branch `main`, carpeta `/ (root)` → Save.
   En 1-2 minutos tendrás tu URL: `https://tuusuario.github.io/turepo/`.

5. Ábrela en el móvil → "Añadir a pantalla de inicio" (iOS) o
   "Instalar app" (Android).

A partir de aquí, GitHub actualiza los precios solo, de lunes a viernes,
a las 18:00 y 20:00 UTC. Nunca tienes que tocar nada más.

## Añadir otro fondo o índice en el futuro

Edita **dos sitios**, siempre en pareja:

1. `scripts/fetch_prices.py` → añade un objeto al array `ASSETS` con el
   ticker de Yahoo Finance (búscalo en https://finance.yahoo.com/lookup
   usando el ISIN).
2. `index.html` → añade el mismo objeto (sin el `ticker`) al array
   `ASSETS` de dentro del `<script>`.

Guarda, sube los cambios, y lanza el workflow a mano una vez
("Run workflow") para generar el primer dato de ese activo nuevo.

## Si algún día deja de funcionar
Los datos vienen de un endpoint no oficial de Yahoo Finance (no hay API
gratuita 100% oficial para fondos OEIC). Si Yahoo cambia algo y el script
empieza a fallar, lo verás en la pestaña Actions (la ejecución saldrá en
rojo) — avísame y lo adaptamos.
