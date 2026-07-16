#!/usr/bin/env python3
"""
Descarga el histórico diario (VL) de cada fondo y lo guarda en /data.
Usa yfinance en vez de llamar a la API de Yahoo a mano: yfinance se
mantiene activamente y sabe gestionar las cookies/crumb que Yahoo exige
ahora para bloquear peticiones automatizadas simples (como las que salen
de una IP de centro de datos, p.ej. GitHub Actions).

Para cada fondo se prueban varios tickers candidatos, por si el símbolo
"obvio" (ISIN + sufijo de bolsa) no es el que usa realmente Yahoo
internamente para fondos de inversión (muchos usan códigos 0P0001XXXX).
Se queda con el primero que devuelva histórico real.
"""
import json
import os
import datetime
import yfinance as yf

ASSETS = [
    {
        "id": "msci_eur",
        "name": "Fidelity MSCI World Index Fund",
        "sub": "P-Acc EUR (sin cobertura de divisa)",
        "isin": "IE00BYX5NX33",
        "candidates": ["IE00BYX5NX33.SG", "0P0001CLDK.F", "IE00BYX5NX33.DE", "IE00BYX5NX33.F"],
    },
    {
        "id": "msci_eur_h",
        "name": "Fidelity MSCI World Index Fund",
        "sub": "P-Acc EUR (hedged / con cobertura)",
        "isin": "IE00BYX5P602",
        "candidates": ["0P0001CJGV.F", "IE00BYX5P602.SG", "IE00BYX5P602.DE"],
    },
    {
        "id": "world_gbp",
        "name": "Fidelity Index World Fund",
        "sub": "P-Acc GBP",
        "isin": "GB00BJS8SJ34",
        "candidates": ["GB00BJS8SJ34.L", "0P000125KV.L", "0P00013O91.L"],
    },
]


def try_fetch(candidates):
    """Prueba cada ticker candidato y devuelve el primero con histórico útil."""
    for ticker in candidates:
        try:
            tk = yf.Ticker(ticker)
            hist = tk.history(period="max", interval="1d", auto_adjust=False)
            if hist is not None and len(hist) >= 5:
                return ticker, tk, hist
            print(f"  {ticker}: respuesta vacía o insuficiente ({0 if hist is None else len(hist)} filas)")
        except Exception as e:
            print(f"  {ticker}: fallo -> {e}")
    return None, None, None


def build_points(hist):
    points = []
    for idx, row in hist.iterrows():
        close = row.get("Close")
        if close is None or (isinstance(close, float) and close != close):  # NaN check
            continue
        ts = int(idx.timestamp())
        points.append({"t": ts, "v": float(close)})
    return points


def build_meta(tk, hist):
    """Intenta sacar metadatos de fast_info; si algo falla, se calcula a
    partir del propio histórico para no depender de una API que puede
    cambiar de forma."""
    meta = {}
    try:
        fi = tk.fast_info
        meta["currency"] = fi.get("currency")
    except Exception:
        meta["currency"] = None

    closes = hist["Close"].dropna()
    meta["regularMarketPrice"] = float(closes.iloc[-1])
    meta["previousClose"] = float(closes.iloc[-2]) if len(closes) > 1 else float(closes.iloc[-1])
    meta["chartPreviousClose"] = meta["previousClose"]
    meta["regularMarketTime"] = int(closes.index[-1].timestamp())

    last_year = closes[closes.index >= (closes.index[-1] - datetime.timedelta(days=365))]
    if len(last_year):
        meta["fiftyTwoWeekLow"] = float(last_year.min())
        meta["fiftyTwoWeekHigh"] = float(last_year.max())

    if not meta.get("currency"):
        meta["currency"] = "EUR"
    return meta


def main():
    os.makedirs("data", exist_ok=True)
    index = []
    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

    for a in ASSETS:
        print(f"Buscando {a['id']} ({a['isin']})...")
        ticker, tk, hist = try_fetch(a["candidates"])

        if ticker is None:
            print(f"ERROR {a['id']}: ningún ticker candidato devolvió datos")
            index.append({**{k: v for k, v in a.items() if k != "candidates"}, "ok": False,
                          "error": "sin datos en ningún ticker candidato"})
            continue

        points = build_points(hist)
        meta = build_meta(tk, hist)

        out = {
            "asset": {k: v for k, v in a.items() if k != "candidates"} | {"ticker": ticker},
            "meta": meta,
            "points": points,
            "updated_at": now,
        }
        with open(f"data/{a['id']}.json", "w") as f:
            json.dump(out, f, separators=(",", ":"))

        index.append({**{k: v for k, v in a.items() if k != "candidates"}, "ticker": ticker,
                       "ok": True, "points": len(points)})
        print(f"OK  {a['id']}: usado {ticker}, {len(points)} puntos")

    with open("data/_index.json", "w") as f:
        json.dump({"assets": index, "updated_at": now}, f, indent=2)


if __name__ == "__main__":
    main()
