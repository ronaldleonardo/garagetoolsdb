#!/usr/bin/env python3
import json, requests, websocket, time, sys

def new_tab():
    r = requests.put("http://127.0.0.1:9222/json/new?about:blank", timeout=10)
    return r.json()["webSocketDebuggerUrl"]

class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=60)
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
        r = self.call("Runtime.evaluate", {"expression": expr, "returnByValue": True})["result"]
        if "exceptionDetails" in r: return None
        return r.get("value")
    def close(self):
        try: self.ws.close()
        except Exception: pass

US_COOKIES = [
    {"name":"lc-main","value":"en_US","url":"https://www.amazon.com/"},
    {"name":"i18n-prefs","value":"USD","url":"https://www.amazon.com/"},
    {"name":"sp-cdn","value":"L5Z9","url":"https://www.amazon.com/"},
    {"name":"session-id","value":"135-6192633-0505308","url":"https://www.amazon.com/"},
]

PROD_JS = """(() => {
    const t=document.title;
    const body=document.body?document.body.innerText:'';
    const title=document.querySelector('#productTitle')?.textContent?.trim() || (document.querySelector('h1')?.textContent?.trim()||'');
    // buybox prices: try specific containers then fallbacks
    const can=[]; const seen=new Set();
    const sel=['#corePrice_feature_div .a-price .a-offscreen',
      '#corePriceDisplay_desktop_feature_div .a-offscreen',
      'span.priceToPay span.a-offscreen',
      '#corePrice_feature_div .a-price',
      '#corePriceDisplay_desktop_feature_div .a-price .a-offscreen',
      '.a-price .a-offscreen'];
    for(const s of sel){const el=document.querySelector(s); if(el){const tx=el.textContent.trim(); if(/\$[0-9]/.test(tx)&&!seen.has(tx)){can.push({s,tx}); seen.add(tx);}}}
    // rating & reviews
    const arEl=document.querySelector('#acrPopover');
    const ar=arEl?arEl.getAttribute('title')?.trim():null;
    const rvEl=document.querySelector('#acrCustomerReviewText');
    const rv=rvEl?rvEl.textContent.trim():null;
    const availability=document.querySelector('#availability')?.textContent?.trim()||'';
    const dead=/Page Not Found|We couldn't find|doesn't exist|dogs of amazon/i.test(t+body)&&!title;
    return {t, title, candidates:can.slice(0,4), ar, rv, availability, dead};
})()"""

def get_product(asin):
    cdp.call("Page.enable"); cdp.call("Runtime.enable"); cdp.call("Network.enable")
    for c in US_COOKIES:
        cdp.call("Network.setCookie", c)
    cdp.call("Page.navigate", {"url": f"https://www.amazon.com/dp/{asin}"})
    for _ in range(14):
        time.sleep(2.5)
        v = cdp.eval("({t:document.title, body:document.body?document.body.innerText.slice(0,250):''})")
        if "robot" in v["t"]+v["body"] or "Continue shopping" in v["body"]:
            cdp.eval("""(() => { const b=[...document.querySelectorAll('button,a')].find(e=>/Continue shopping/i.test(e.textContent)); if(b){b.click();return 'c';} return 'nf'; })()""")
            time.sleep(2)
        if "Amazon" in v["t"] and v["body"].strip():
            break
    return cdp.eval(PROD_JS)

if __name__ == "__main__":
    asins = json.loads(sys.argv[1])
    ws = new_tab(); cdp = CDP(ws)
    out=[]
    for a in asins:
        try: out.append({"asin":a, **get_product(a)})
        except Exception as e: out.append({"asin":a, "error":str(e)})
        time.sleep(1)
    cdp.close()
    print(json.dumps(out, indent=2))