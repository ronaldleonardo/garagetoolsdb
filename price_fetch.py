#!/usr/bin/env python3
"""Fetch live Amazon US buybox prices for a list of ASINs.

Route 1 (primary, verified 2026-10-10..13):
  Firecrawl LAN (192.168.18.4:3002) POST /v1/scrape on
  https://www.amazon.com/gp/aw/d/<ASIN>   <- mobile "aw" PDP, not bot-walled

Route 2 (FALLBACK, verified 2026-10-14):
  https://r.jina.ai/https://www.amazon.com/gp/aw/d/<ASIN>   (anonymous, no key)
  Firecrawl started returning a degraded page for BULKY items (air compressors):
  the buybox is replaced by outOfStockBuyBox_feature_div plus
  "This item cannot be shipped to your selected delivery location"
  (its egress has no proper US delivery ZIP for heavy items). Jina's fetch
  resolves to a real US location ("Delivering to The Dalles 97058") and renders
  the full buybox, including a desktop_buybox_group_1 JSON blob. So: whenever
  Firecrawl yields no price / shows the ship-block message, retry via jina
  before calling the product unverified. Lightweight items still work on
  route 1, jina is just the fallback (be polite: ~6s between jina calls).

The price lives in an escaped JSON blob in the markdown:
  mobile_buybox_group_1   (route 1)  or  desktop_buybox_group_1 (route 2)
  {"displayPrice":"$24.69","priceAmount":24.69,...}

Routes that are DEAD, do not waste time on them:
  - r.jina.ai/<dp url>          -> "Continue shopping" wall
  - r.jina.ai/<s?k= search>     -> intermittent, mostly walled now
  - Firecrawl /clp/<ASIN>       -> 404, route removed
  - Firecrawl /dp/<ASIN>        -> bot wall (UA header does not help)
  - Firecrawl proxy=stealth     -> 500 on this server
  - /gp/aod/ajax, /gp/offer-listing, /gp/aw/ol -> 344-byte empty stub
  - SerpAPI                     -> key exhausted
  - camelcamelcamel via proxy   -> security verification block

Usage:
  python3 price_fetch.py B01FW3U26G B005GLQCKA ...
  python3 price_fetch.py --json '{"B01FW3U26G": 23.08, ...}'   # compare against stored
"""
import json, re, sys, time, urllib.request

FIRECRAWL = "http://192.168.18.4:3002/v1/scrape"
JINA = "https://r.jina.ai/https://www.amazon.com/gp/aw/d/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


def fetch(asin, tries=4, gap=8, timeout=120):
    """Return markdown for the mobile PDP via Firecrawl, or '' on failure."""
    for _ in range(tries):
        try:
            req = urllib.request.Request(
                FIRECRAWL,
                data=json.dumps({
                    "url": f"https://www.amazon.com/gp/aw/d/{asin}",
                    "formats": ["markdown"],
                }).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            r = urllib.request.urlopen(req, timeout=timeout)
            md = json.loads(r.read().decode("utf-8", "ignore")).get("data", {}).get("markdown", "")
            if len(md) > 5000 and "$" in md:
                return md
        except Exception:
            pass
        time.sleep(gap)
    return ""


def jina_fetch(asin, tries=3, gap=10, timeout=150):
    """Fallback: r.jina.ai on the mobile PDP. Anonymous, ~20 req/min cap."""
    for _ in range(tries):
        try:
            req = urllib.request.Request(
                JINA + asin, headers={"User-Agent": UA})
            md = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")
            if len(md) > 5000:
                return md
        except Exception:
            pass
        time.sleep(gap)
    return ""


def parse(md, asin):
    """Extract buybox price and metadata. Returns dict."""
    out = {"asin": asin}

    # 1. buybox JSON blob, backslashes are markdown escaping. Most reliable.
    #    Route 1 renders mobile_buybox_group_1, route 2 renders desktop_buybox_group_1.
    m = re.search(
        r'(?:mobile|desktop)\\*_buybox\\*_group\\*_1\\*"?:\s*\\*\[\s*\\*\{\s*\\*"displayPrice\\*":\s*\\*"\$([\d,]+\.\d\d)',
        md)
    if m:
        m2 = re.search(
            r'\\*"priceAmount\\*":\s*([\d.]+)', md[m.start():m.start() + 400])
        out["price"] = float(m2.group(1)) if m2 else float(m.group(1).replace(",", ""))
        out["price_src"] = "buybox_json"
    else:
        # 2. fallback: "X with N percent savings"
        m = re.search(r'\$([\d,]+\.\d\d) with \d+ percent savings', md)
        if m:
            out["price"] = float(m.group(1).replace(",", ""))
            out["price_src"] = "savings_line"

    m = re.search(r'List Price: \$([\d,]+\\.?\d*\d)', md)
    if m:
        out["list_price"] = m.group(1)

    # ASIN guard: the brand store link carries lp_asin, confirms the right PDP
    out["asin_confirmed"] = f"lp_asin={asin}" in md

    out["in_stock"] = "In Stock" in md
    out["ship_block"] = "cannot be shipped to your selected delivery location" in md
    out["is_prime"] = "Or Prime members get FREE delivery" in md

    m = re.search(r'([\d.]+) out of 5 stars', md)
    if m:
        out["rating"] = m.group(1)

    m = re.search(r'([\d,]+) ratings', md)
    if m:
        out["reviews"] = m.group(1)
    return out


def main():
    args = sys.argv[1:]
    stored = {}
    if args and args[0] == "--json":
        stored = {k: float(str(v).replace("$", "")) for k, v in json.loads(args[1]).items()}
        asins = list(stored)
    else:
        asins = args

    results = {}
    for asin in asins:
        md = fetch(asin)
        src_route = "firecrawl"
        if not md:
            print(f"{asin}  firecrawl failed, trying jina...")
            md = jina_fetch(asin)
            src_route = "jina"
        p = parse(md, asin) if md else {"asin": asin}
        # Firecrawl gives a degraded page (no buybox / ship-blocked) for bulky items:
        # retry the same PDP through jina before declaring it unverified.
        if md and "price" not in p and src_route == "firecrawl":
            jmd = jina_fetch(asin)
            if jmd:
                jp = parse(jmd, asin)
                if "price" in jp:
                    p = jp
                    src_route = "jina"
        if not md:
            results[asin] = {"asin": asin, "error": "fetch failed on all retries"}
            print(f"{asin}  FETCH FAILED")
            continue
        results[asin] = p
        p["route"] = src_route
        line = f"{asin}  [{src_route}]  "
        if "price" in p:
            line += f"live ${p['price']:.2f}  ({p['price_src']})"
            if asin in stored:
                old = float(str(stored[asin]).replace("$", ""))
                pct = (p["price"] - old) / old * 100
                p["stored"] = old
                p["pct_change"] = round(pct, 2)
                p["action"] = "EDIT" if abs(pct) >= 10 else "skip (<10%)"
                line += f"  stored ${old:.2f}  {pct:+.2f}%  {p['action']}"
        else:
            line += "NO PRICE PARSED"
        if not p.get("asin_confirmed"):
            line += "  [WARN asin not confirmed]"
        if p.get("ship_block"):
            line += "  [WARN delivery-location ship block]"
        if not p.get("in_stock"):
            line += "  [WARN not in stock]"
        print(line)

    print("\n" + json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
