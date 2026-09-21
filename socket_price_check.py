#!/usr/bin/env python3
"""SerpAPI check for socket-set products against current data.mjs prices."""
import json, sys, time, urllib.request, urllib.parse, os

API_KEY = os.environ.get("SERPAPI_API_KEY", "")

products = [
    ("GEARWRENCH 124PC", "GEARWRENCH 124 piece socket set", "B000VDXSV6", "$149.99"),
    ("DEWALT 102PC Set", "DEWALT 102 piece socket set SAE metric", "B0BVMKKTZ1", "$79.99"),
    ("TEKTON 3/8 Drive", "TEKTON 3/8 inch drive socket set 18 piece", "B07Q35CQ2V", "$29.99"),
    ("Sunex 2598 Master", "Sunex 2598 master socket set 258 piece", "B00A1W3G8E", "$349.99"),
    ("QUINN 132PC Kit", "QUINN 132 piece socket set Harbor Freight", "B0B5WBHK4B", "$99.99"),
]

def serp_search(q, retries=3):
    params = {"engine": "amazon", "k": q, "api_key": API_KEY}
    url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            print(f"    [retry {attempt+1}] {e}", file=sys.stderr)
            time.sleep(4)
    return {"error": "failed after retries"}

def price_to_float(s):
    s = str(s).replace("$", "").replace(",", "").strip()
    try:
        return float(s)
    except Exception:
        return None

for name, search_term, cur_asin, cur_price in products:
    print(f"=== {name} ===")
    print(f"  current: {cur_price} ({cur_asin})")
    result = serp_search(search_term)
    if "error" in result or result.get("search_metadata", {}).get("status") != "Success":
        print(f"  ERROR: {result.get('error', 'non-success')}")
        time.sleep(3)
        continue
    organic = result.get("organic_results", [])
    if not organic:
        print(f"  No organic results")
        time.sleep(3)
        continue
    first = organic[0]
    got_asin = first.get("asin")
    got_price = first.get("price")
    got_title = first.get("title", "")[:100]
    cur = price_to_float(cur_price)
    got = price_to_float(got_price)
    pct = f"{abs(got-cur)/cur*100:.1f}%" if (cur and got) else "n/a"
    print(f"  GOT: price={got_price} asin={got_asin} pct_vs_current={pct}")
    print(f"  title: {got_title}")
    print(f"  ASIN match current: {got_asin == cur_asin}")
    time.sleep(3)