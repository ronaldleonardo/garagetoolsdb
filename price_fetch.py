#!/usr/bin/env python3
"""Fetch live Amazon US buybox prices for a list of ASINs.

Route that works from this LXC (verified 2026-10-11):
  Firecrawl LAN (192.168.18.4:3002) POST /v1/scrape on
  https://www.amazon.com/gp/aw/d/<ASIN>   <- mobile "aw" PDP, not bot-walled

Routes that are DEAD, do not waste time on them:
  - r.jina.ai/<dp url>          -> "Continue shopping" wall
  - r.jina.ai/<s?k= search>     -> intermittent, mostly walled now
  - Firecrawl /clp/<ASIN>       -> 404, route removed
  - SerpAPI                     -> key exhausted
  - camelcamelcamel via proxy   -> security verification block

The price lives in an escaped JSON blob in the markdown:
  {\"mobile\_buybox\_group\_1\":\[{\"displayPrice\":\"$24.69\",\"priceAmount\":24.69,...}

Usage:
  python3 price_fetch.py B01FW3U26G B005GLQCKA ...
  python3 price_fetch.py --json '{"B01FW3U26G": 23.08, ...}'   # compare against stored
"""
import json, re, sys, time, urllib.request

FIRECRAWL = "http://192.168.18.4:3002/v1/scrape"


def fetch(asin, tries=4, gap=8, timeout=120):
    """Return markdown for the mobile PDP, or '' on failure."""
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


def parse(md, asin):
    """Extract buybox price and metadata. Returns dict."""
    out = {"asin": asin}

    # 1. buybox JSON blob, backslashes are markdown escaping. Most reliable.
    m = re.search(
        r'mobile\\?_buybox\\?_group\\?_1\\?"?:\\?\[\\?\{\\?"displayPrice\\?":\\?"\$([\d,]+\.\d\d)\\?",'
        r'\\?"priceAmount\\?":([\d.]+)', md)
    if m:
        out["price"] = float(m.group(2))
        out["price_src"] = "buybox_json"
    else:
        # 2. fallback: "X with N percent savings"
        m = re.search(r'\$([\d,]+\.\d\d) with \d+ percent savings', md)
        if m:
            out["price"] = float(m.group(1).replace(",", ""))
            out["price_src"] = "savings_line"

    m = re.search(r'List Price: \$([\d,]+\.\d\d)', md)
    if m:
        out["list_price"] = m.group(1)

    # ASIN guard: the brand store link carries lp_asin, confirms the right PDP
    out["asin_confirmed"] = f"lp_asin={asin}" in md

    out["in_stock"] = "In Stock" in md
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
        if not md:
            results[asin] = {"asin": asin, "error": "fetch failed on all retries"}
            print(f"{asin}  FETCH FAILED")
            continue
        p = parse(md, asin)
        results[asin] = p
        line = f"{asin}  "
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
        if not p.get("in_stock"):
            line += "  [WARN not in stock]"
        print(line)

    print("\n" + json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
