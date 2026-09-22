#!/usr/bin/env python3
"""CDP breaker check v2: realistic UA + click-through bot wall, longer wait."""
import json, time, requests, websocket

CDP_HTTP = "http://127.0.0.1:9222"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36")

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
        return self.call("Runtime.evaluate", {"expression": expr, "returnByValue": True})["result"]["value"]
    def close(self):
        try: self.ws.close()
        except Exception: pass

ws_url = new_tab()
cdp = CDP(ws_url)
cdp.call("Page.enable"); cdp.call("Runtime.enable")
cdp.call("Network.enable")
cdp.call("Network.setUserAgentOverride", {"userAgent": UA, "platform": "Win32"})

def nav(asin):
    cdp.call("Page.navigate", {"url": f"https://www.amazon.com/dp/{asin}"})
    # poll up to 25s for either real product page or bot wall
    for _ in range(10):
        time.sleep(2.5)
        v = cdp.eval("({t:document.title, body:document.body?document.body.innerText.slice(0,300):''})")
        # bot wall present?
        if "Continue shopping" in v["body"] and "I am not a robot" not in v["body"]:
            cdp.eval("""(() => {
                const els=[...document.querySelectorAll('button, a, input')];
                const b=els.find(e=>/Continue shopping/i.test(e.textContent));
                if(b){b.click(); return 'clicked';} return 'notfound';
            })()""")
            time.sleep(3)
        if "Amazon.com" in v["t"] and "Continue shopping" not in v["body"] and v["body"].strip():
            break
    return cdp.eval("""(() => {
        const t=document.title; const h=location.href;
        const body=document.body?document.body.innerText:'';
        const pSels=['#corePrice_feature_div .a-price .a-offscreen','#corePriceDisplay_desktop_feature_div .a-offscreen','span.priceToPay span.a-offscreen','#price_inside_buybox','span.a-price span.a-offscreen'];
        let price=null;
        for(const s of pSels){const el=document.querySelector(s); if(el&&el.textContent.trim()){price=el.textContent.trim();break;}}
        const dead = /(Page Not Found|We couldn't find|Sorry, we just need to make sure|To discuss|this page doesn't seem to exist)/i.test(t+body);
        return {t, h, price, dead, body_starts: body.slice(0,120)};
    })()""")

products = [
    ("TEKTON 1/2 Breaker", "B07C9B7Z8W"),
    ("GEARWRENCH 1/2", "B000VDXSV6"),
    ("Capri Tools 3/8", "B07D3M64K5"),
    ("Sunex 1/2 Impact", "B00A1W3G8E"),
    ("SK Hand Tool 3/4", "B0002NYWQ2"),
]
out = []
for name, asin in products:
    try:
        v = nav(asin)
        out.append({"name": name, "asin": asin, **v})
    except Exception as e:
        out.append({"name": name, "asin": asin, "error": str(e)})
    time.sleep(2)
cdp.close()
print(json.dumps(out, indent=2))