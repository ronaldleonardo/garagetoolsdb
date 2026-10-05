#!/usr/bin/env python3
"""Fetch Amazon CLP via Firecrawl and extract the main product price."""
import json, re, sys, time, subprocess

FC = "http://192.168.18.4:3002/v2/scrape"

def scrape(url, wait=2500, fmt="markdown", timeout=80):
    payload = json.dumps({"url": url, "formats": [fmt], "waitFor": wait})
    p = subprocess.run(["curl", "-s", "--max-time", str(timeout), "-X", "POST", FC,
                        "-H", "Content-Type: application/json", "-d", payload],
                       capture_output=True, text=True)
    try:
        d = json.loads(p.stdout)
    except Exception:
        return None
    return d

def prices_from_md(md):
    md = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', md)
    # strip markdown link targets
    return re.findall(r'\$\s?\d[\d,]*(?:\.\d{2})?', md)

def main():
    asins = json.loads(sys.argv[1])
    out = {}
    for a in asins:
        d = scrape(f"https://www.amazon.com/clp/{a}")
        rec = {"asin": a}
        if not d or not d.get("success"):
            rec["error"] = (d or {}).get("error", "no-response")
            out[a] = rec
            print(json.dumps(rec)); continue
        data = d["data"]; md = data.get("markdown") or ""
        meta = data.get("metadata", {})
        rec["status"] = meta.get("statusCode")
        rec["title"] = (meta.get("title") or "").strip()[:160]
        # your-pick card block
        i = md.find("Your pick")
        if i >= 0:
            card = re.sub(r'\s+', ' ', md[i:i+1400])
            card = re.sub(r'\(https?://[^)]*\)', '(…)', card)
            rec["card"] = card[:600]
        rec["prices"] = prices_from_md(md)[:12]
        out[a] = rec
        print(json.dumps(rec))
        time.sleep(1)
    with open("/root/garagetoolsdb/.clp_out.json", "w") as f:
        json.dump(out, f, indent=1)

if __name__ == "__main__":
    main()
