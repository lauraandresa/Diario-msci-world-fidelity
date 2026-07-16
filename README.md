# Ledger — seguimiento diario de tu fondo Fidelity

## Qué es esto
Una PWA (app web instalable) que muestra el valor liquidativo diario de tu
fondo indexado, sin backend propio: GitHub descarga el precio por ti una vez
al día y tu móvil solo lee ese archivo.


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
