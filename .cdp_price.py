#!/usr/bin/env python3
import json, time, requests, websocket, sys

CDP_HTTP = "http://127.0.0.1:9222"

def new_tab():
    r = requests.put(f"{CDP_HTTP}/json/new?about:blank", timeout=10)
    return r.json()["webSocketDebuggerUrl"]

class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=90)
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
        if "exceptionDetails" in r: return "EXC:"+json.dumps(r["exceptionDetails"])[:200]
        return r.get("value")
    def close(self):
        try: self.ws.close()
        except Exception: pass

def nav(asin):
    cdp.call("Page.enable"); cdp.call("Runtime.enable")
    cdp.call("Page.navigate", {"url": f"https://www.amazon.com/dp/{asin}"})
    for _ in range(14):
        time.sleep(2.5)
        v = cdp.eval("({t:document.title, h:location.href, body:document.body?document.body.innerText.slice(0,400):''})")
        # click through bot wall if present
        if "Continue shopping" in v["body"] and "robot" not in v["body"]:
            cdp.eval("""(() => { const b=[...document.querySelectorAll('button,a')].find(e=>/Continue shopping/i.test(e.textContent)); if(b){b.click(); return 'clicked';} return 'nf'; })()""")
            time.sleep(3)
        if "Amazon" in v["t"] and "Continue shopping" not in v["body"] and v["body"].strip():
            break
    return cdp.eval("""(() => {
        const t=document.title, h=location.href;
        const body=document.body?document.body.innerText:'';
        const pSels=['#corePrice_feature_div .a-price .a-offscreen','#corePriceDisplay_desktop_feature_div .a-offscreen','span.priceToPay span.a-offscreen','#price_inside_buybox','.apexPriceToPay .a-offscreen','#corePrice_feature_div .a-price'];
        let price=null;
        for(const s of pSels){const el=document.querySelector(s); if(el){price=el.textContent.trim(); if(price.includes('$')) break;}}
        // rating & reviews
        const ar=document.querySelector('#acrPopover') ? document.querySelector('#acrPopover').getAttribute('title') : null;
        const rv=document.querySelector('#acrCustomerReviewText') ? document.querySelector('#acrCustomerReviewText').textContent.trim() : null;
        const dead=/Page Not Found|We couldn't find|doesn't exist|dogs of amazon/i.test(t+body);
        const brand=/^Amazon\.com$/i.test(t);
        return {t, h, price, ar, rv, dead};
    })()""")

if __name__ == "__main__":
    asins = json.loads(sys.argv[1])
    ws = new_tab()
    cdp = CDP(ws)
    out=[]
    for a in asins:
        try:
            out.append({"asin":a, **nav(a)})
        except Exception as e:
            out.append({"asin":a, "error":str(e)})
        time.sleep(1.5)
    cdp.close()
    print(json.dumps(out, indent=2))