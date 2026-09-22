#!/usr/bin/env python3
import json, time, requests, websocket
CDP_HTTP = "http://127.0.0.1:9222"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36")
def new_tab():
    r = requests.put(f"{CDP_HTTP}/json/new?about:blank", timeout=10)
    return r.json()["webSocketDebuggerUrl"]
class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=90); self.msg_id = 0
    def call(self, m, p=None):
        self.msg_id += 1; mid = self.msg_id
        self.ws.send(json.dumps({"id": mid, "method": m, "params": p or {}}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg: raise RuntimeError(f"{m}: {msg['error']}")
                return msg.get("result", {})
    def ev(self, e):
        return self.call("Runtime.evaluate", {"expression": e, "returnByValue": True})["result"]["value"]
    def close(self):
        try: self.ws.close()
        except Exception: pass

ws = new_tab(); c = CDP(ws)
c.call("Page.enable"); c.call("Runtime.enable"); c.call("Network.enable")
c.call("Network.setUserAgentOverride", {"userAgent": UA, "platform": "Win32"})
def nav(asin):
    c.call("Page.navigate", {"url": f"https://www.amazon.com/dp/{asin}"})
    for _ in range(10):
        time.sleep(2.5)
        v = c.ev("({t:document.title,body:document.body?document.body.innerText.slice(0,150):''})")
        if "Continue shopping" in v["body"]:
            c.ev("""(()=>{const b=[...document.querySelectorAll('button,a,input')].find(e=>/Continue shopping/i.test(e.textContent));if(b){b.click();return 1}return 0})()""")
            time.sleep(3)
        if v["body"].strip() and "Continue shopping" not in v["body"]: break
    return c.ev("""(()=>{const sels=['#corePrice_feature_div .a-price .a-offscreen','#corePriceDisplay_desktop_feature_div .a-offscreen','span.priceToPay span.a-offscreen','#price_inside_buybox','span.a-price span.a-offscreen'];let p=null;for(const s of sels){const e=document.querySelector(s);if(e&&e.textContent.trim()){p=e.textContent.trim();break}}return {t:document.title.slice(0,70),p}})()""")
out = []
for i in range(2):
    try: out.append(nav("B01G5EA74I"))
    except Exception as e: out.append({"error": str(e)})
    time.sleep(2)
c.close(); print(json.dumps(out, indent=2))