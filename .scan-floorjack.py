#!/usr/bin/env python3
"""GTDB price search script - search Amazon via SerpAPI for product current prices."""
import json, sys, time, urllib.request, urllib.parse

API_KEY = "ca2313d149898bbb02c72d8a7f602ef7fe0ee971f07549de64f9049b22ffef46"

def serp_search(query, retries=3):
    params = {
        "engine": "amazon",
        "k": query,
        "api_key": API_KEY,
    }
    url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            print(f"  [retry {attempt+1}] error: {e}", file=sys.stderr)
            time.sleep(3)
    return {"error": "failed after retries"}

PRODUCTS = [
    {"name": "Daytona 3 Ton",     "query": "Daytona 3 Ton Professional Rapid Pump Floor Jack",   "asin_old": "B01N57DPH7"},
    {"name": "Pittsburgh 1.5 Ton","query": "Pittsburgh Automotive 1.5 Ton Aluminum Floor Jack",  "asin_old": "B000COC6R4"},
    {"name": "Torin Big Red 2 Ton","query": "Torin Big Red 2 Ton Floor Jack",                    "asin_old": "B00413C5VY"},
    {"name": "JEGS 2 Ton Aluminum","query": "JEGS 2 Ton Aluminum Floor Jack",                    "asin_old": "B0012TQ3J8"},
    {"name": "ARCAN 3 Ton",       "query": "ARCAN 3 Ton Floor Jack",                            "asin_old": "B0042AMGIMU"},
]

out = []
for p in PRODUCTS:
    print(f"\n=== {p['name']} (old ASIN {p['asin_old']}) ===")
    d = serp_search(p["query"])
    if "error" in d:
        print("  ERROR:", d["error"])
        continue
    org = d.get("organic_results", [])
    # find best match: prefer exact ASIN, then title match
    best = None
    for r in org:
        if r.get("asin") == p["asin_old"]:
            best = r
            break
    if best is None and org:
        best = org[0]
    if best:
        rec = {
            "product": p["name"],
            "title": best.get("title", "?"),
            "asin": best.get("asin", "?"),
            "price": best.get("price", best.get("price_str", "?")),
            "rating": best.get("rating", "?"),
            "reviews": best.get("reviews", "?"),
            "url": best.get("link", "?"),
            "thumbnail": best.get("thumbnail", "?"),
            "exact_asin": best.get("asin") == p["asin_old"],
        }
        out.append(rec)
        print(f"  -> {rec['title']}")
        print(f"     ASIN: {rec['asin']} (exact: {rec['exact_asin']}) | Price: {rec['price']} | Rating: {rec['rating']} | Reviews: {rec['reviews']}")
    time.sleep(2)

with open("/root/garagetoolsdb/.price-scan-floorjack.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nSaved to /root/garagetoolsdb/.price-scan-floorjack.json")