#!/usr/bin/env python3
import json, requests, websocket, time, sys, urllib.parse

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
SEARCH_JS = """(() => {
  return [...document.querySelectorAll('div[data-component-type="s-search-result"]')].slice(0,8).map(c => {
    const a=c.querySelector('h2 a');
    const title=(a? (a.getAttribute('title')||a.textContent||'') : (c.querySelector('h2')?.textContent||'')).trim();
    const p=c.querySelector('.a-price .a-offscreen')?.textContent?.trim()||'';
    const rvEl=c.querySelector('div[data-cy="reviews-block"] span.a-size-base, span[aria-label*="ratings"], a[href*="customerReviews"]')?.textContent?.trim()||'';
    const arEl=c.querySelector('span.a-icon-alt')?.textContent?.trim()||'';
    return {asin:c.getAttribute('data-asin')||'', title:title.slice(0,110), p, ar:arEl.slice(0,25), rv:rvEl.slice(0,25)};
  }).filter(x=>x.asin);
})()"""

def search(q):
    cdp.call("Page.enable"); cdp.call("Runtime.enable"); cdp.call("Network.enable")
    for c in US_COOKIES: cdp.call("Network.setCookie", c)
    cdp.call("Page.navigate", {"url": "https://www.amazon.com/s?k="+urllib.parse.quote(q)})
    for _ in range(12):
        time.sleep(2.5)
        v=cdp.eval("({t:document.title, body:document.body?document.body.innerText.slice(0,180):''})")
        if "robot" in v["t"]+v["body"] or "Continue shopping" in v["body"]:
            cdp.eval("""(() => { const b=[...document.querySelectorAll('button,a')].find(e=>/Continue shopping/i.test(e.textContent)); if(b){b.click();return'c';} return'nf'; })()""")
            time.sleep(2)
        if "Amazon" in v["t"] and v["body"].strip(): break
    return cdp.eval(SEARCH_JS)

if __name__=="__main__":
    qs=json.loads(sys.argv[1])
    ws=new_tab(); cdp=CDP(ws); out=[]
    for q in qs:
        try: out.append({"q":q,"r":search(q)})
        except Exception as e: out.append({"q":q,"e":str(e)})
        time.sleep(1)
    cdp.close(); print(json.dumps(out, indent=1))