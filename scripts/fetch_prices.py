#!/usr/bin/env python3
"""
Descarga el histórico diario (VL) de cada fondo desde Yahoo Finance y lo
guarda como JSON dentro de /data. Este script lo ejecuta GitHub Actions
(no tu móvil), así que no hay problema de CORS: es una llamada servidor-a-servidor.

Pide el rango "max" una sola vez por fondo: con el histórico completo diario
el cliente (la app) puede recortar 5D/1M/6M/YTD/1A/5A sin volver a pedir nada.
"""
import json
import os
import urllib.request
import datetime

ASSETS = [
    {"id": "msci_eur", "name": "Fidelity MSCI World Index Fund",
     "sub": "P-Acc EUR (sin cobertura de divisa)", "isin": "IE00BYX5NX33",
     "ticker": "IE00BYX5NX33.SG"},
    {"id": "msci_eur_h", "name": "Fidelity MSCI World Index Fund",
     "sub": "P-Acc EUR (hedged / con cobertura)", "isin": "IE00BYX5P602",
     "ticker": "IE00BYX5P602.SG"},
    {"id": "world_gbp", "name": "Fidelity Index World Fund",
     "sub": "P-Acc GBP", "isin": "GB00BJS8SJ34",
     "ticker": "GB00BJS8SJ34.L"},
]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; personal-fund-tracker/1.0)"}


def fetch(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=max&interval=1d"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def main():
    os.makedirs("data", exist_ok=True)
    index = []
    now = datetime.datetime.utcnow().isoformat() + "Z"

    for a in ASSETS:
        try:
            raw = fetch(a["ticker"])
            result = raw["chart"]["result"][0]
            ts = result.get("timestamp", [])
            closes = result["indicators"]["quote"][0].get("close", [])
            points = [{"t": t, "v": c} for t, c in zip(ts, closes) if c is not None]

            out = {
                "asset": a,
                "meta": result.get("meta", {}),
                "points": points,
                "updated_at": now,
            }
            with open(f"data/{a['id']}.json", "w") as f:
                json.dump(out, f, separators=(",", ":"))

            index.append({**a, "ok": True, "points": len(points)})
            print(f"OK  {a['id']}: {len(points)} puntos")
        except Exception as e:
            index.append({**a, "ok": False, "error": str(e)})
            print(f"ERROR {a['id']}: {e}")

    with open("data/_index.json", "w") as f:
        json.dump({"assets": index, "updated_at": now}, f, indent=2)


if __name__ == "__main__":
    main()
