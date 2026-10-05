#!/usr/bin/env python3
"""Robust CDP scraper for GTDB price refresh.
Usage:
  python3 .cdp_gtdb.py dp  '["B07W8KJH44", ...]'
  python3 .cdp_gtdb.py search '[{"q":"NOCO Boost X GBX45","want":"GBX45"}, ...]'
"""
import json, time, requests, websocket, sys
from urllib.parse import quote as _q

CDP_HTTP = "http://127.0.0.1:9222"

def pick_target():
    """Reuse an existing page target instead of spawning new tabs."""
    try:
        lst = requests.get(f"{CDP_HTTP}/json/list", timeout=15).json()
    except Exception:
        lst = []
    pref = None
    for t in lst:
        if t.get("type") != "page":
            continue
        u = t.get("url") or ""
        if "amazon.com/dp" in u or u == "about:blank":
            pref = t
            break
    if pref is None:
        for t in lst:
            if t.get("type") == "page":
                pref = t
                break
    if pref is None:
        pref = requests.put(f"{CDP_HTTP}/json/new?about:blank", timeout=15).json()
    return pref["webSocketDebuggerUrl"]

def cleanup(keep_id=None):
    try:
        lst = requests.get(f"{CDP_HTTP}/json/list", timeout=15).json()
    except Exception:
        return
    for t in lst:
        if t.get("type") != "page":
            continue
        u = t.get("url") or ""
        if u == "about:blank" or "amazon.com" in u:
            requests.get(f"{CDP_HTTP}/json/close/{t['id']}", timeout=8)


class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=120)
        self.msg_id = 0
    def call(self, method, params=None):
        self.msg_id += 1; mid = self.msg_id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg: raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})
    def eval(self, expr):
        r = self.call("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})["result"]
        if "exceptionDetails" in r: return {"__exc__": json.dumps(r["exceptionDetails"])[:300]}
        return r.get("value")
    def close(self):
        try: self.ws.close()
        except Exception: pass

def prep(cdp):
    cdp.call("Page.enable"); cdp.call("Runtime.enable"); cdp.call("Network.enable")
    for name, val in [("i18n-prefs", "USD"), ("lc-main", "en_US")]:
        try: cdp.call("Network.setCookie", {"name": name, "value": val, "domain": ".amazon.com", "path": "/"})
        except Exception: pass

def nav(cdp, url, tries=14):
    cdp.call("Page.navigate", {"url": url})
    for _ in range(tries):
        time.sleep(2.2)
        v = cdp.eval("({t:document.title, h:location.href, wall:(document.body?/Continue shopping/.test(document.body.innerText):false)})")
        if isinstance(v, dict) and v.get("wall"):
            cdp.eval("""(() => { const b=[...document.querySelectorAll('button,a,input')].find(e=>/Continue shopping/i.test(e.textContent||e.value||'')); if(b){b.click(); return 'clicked';} return 'nf'; })()""")
            time.sleep(3); continue
        if isinstance(v, dict) and v.get("t") and "Amazon" in v["t"]:
            break
    time.sleep(1)
    return cdp.eval(DP_EXTRACT)

DP_EXTRACT = r"""(() => {
  const t=document.title, h=location.href;
  const body=document.body?document.body.innerText:'';
  const num = s => { if(!s) return null; const x=parseFloat(s.replace(/[^0-9.]/g,'')); return isNaN(x)?null:x; };
  // JSON-LD offers
  let ldPrice=null, ldName=null;
  for (const s of document.querySelectorAll('script[type="application/ld+json"]')) {
    try { const j=JSON.parse(s.textContent); const arr=Array.isArray(j)?j:[j];
      for (const o of arr) { if(o && o.offers){ const of=Array.isArray(o.offers)?o.offers[0]:o.offers; if(of && of.price){ ldPrice=of.price; } } if(o && o.name) ldName=o.name; }
    } catch(e){}
  }
  let price=null, psel=null;
  const sels = ['#corePriceDisplay_desktop_feature_div .a-price .a-offscreen','#corePrice_feature_div .a-price .a-offscreen','#apex_desktop .a-price .a-offscreen','span.priceToPay span.a-offscreen','#price_inside_buybox','#tp_price_block_total_price_ww .a-offscreen','#buybox .a-price .a-offscreen'];
  for (const s of sels) { const el=document.querySelector(s); if(el&&el.textContent.includes('$')){ price=el.textContent.trim(); psel=s; break; } }
  // whole-price-block text (may include cents in sibling)
  let whole=null;
  const wb=document.querySelector('#corePriceDisplay_desktop_feature_div');
  if(wb){ whole=(wb.innerText||'').replace(/\s+/g,' ').slice(0,120); }
  const ar=document.querySelector('#acrPopover')?document.querySelector('#acrPopover').getAttribute('title'):null;
  const rv=document.querySelector('#acrCustomerReviewText')?document.querySelector('#acrCustomerReviewText').textContent.trim():null;
  const byline=document.querySelector('#bylineInfo')?document.querySelector('#bylineInfo').textContent.trim():null;
  const dead=/Page Not Found|We couldn't find|doesn't exist|dogs of amazon/i.test(t+body);
  return {t, h, title:(document.getElementById('productTitle')||{}).textContent?document.getElementById('productTitle').textContent.trim():null,
          price, priceNum:num(price), ldPrice, ldPriceNum:num(ldPrice), psel, whole, ar, rv, byline, dead,
          amazonChoice:/Amazon's Choice/i.test(body), snip: body.slice(0,200)};
})()"""

SEARCH_EXTRACT = r"""(() => {
  const out=[];
  const cards=[...document.querySelectorAll('div[data-asin][data-component-type="s-search-result"]')].slice(0,8);
  for(const c of cards){
    const asin=c.getAttribute('data-asin');
    const title=(c.querySelector('h2 span')||c.querySelector('h2')||{}).textContent||'';
    let price=null; const po=c.querySelector('.a-price .a-offscreen'); if(po&&po.textContent.includes('$')) price=po.textContent.trim();
    const rv=c.querySelector('[data-component-type="s-client-side-analytics"] span.a-size-base')||c.querySelector('span.a-size-base.s-underline-text');
    out.push({asin, title:title.trim().slice(0,120), price});
  }
  return {url:location.href, title:document.title, results:out, wall:/Continue shopping/i.test(document.body.innerText)};
})()"""

if __name__ == "__main__":
    mode = sys.argv[1]
    jobs = json.loads(sys.argv[2])
    cleanup()
    time.sleep(1)
    ws = pick_target()
    cdp = CDP(ws)
    prep(cdp)
    out = []
    for j in jobs:
        if isinstance(j, str):
            j = {"asin": j}
        if mode == "dp":
            url = f"https://www.amazon.com/dp/{j['asin']}"
            try: out.append({"asin": j['asin'], **nav(cdp, url)})
            except Exception as e: out.append({"asin": j['asin'], "error": str(e)})
        else:
            url = "https://www.amazon.com/s?k=" + _q(j["q"])
            try:
                nav(cdp, url, tries=10)
                r = cdp.eval(SEARCH_EXTRACT)
                out.append({"q": j["q"], **r})
            except Exception as e:
                out.append({"q": j["q"], "error": str(e)})
        time.sleep(1)
    cdp.close()
    print(json.dumps(out, indent=1))
