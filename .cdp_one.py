#!/usr/bin/env python3
import json, requests, websocket, time, sys

def new_tab():
    r = requests.put("http://127.0.0.1:9222/json/new?about:blank", timeout=10)
    return r.json()["webSocketDebuggerUrl"]

class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=60); self.nid=1
    def call(self, m, p=None):
        i=self.nid; self.nid+=1
        self.ws.send(json.dumps({"id":i,"method":m,"params":p or {}}))
        while True:
            msg=json.loads(self.ws.recv())
            if msg.get("id")==i:
                if "error" in msg: raise RuntimeError(f"{m}: {msg['error']}")
                return msg.get("result",{})
    def eval(self, x):
        r=self.call("Runtime.evaluate",{"expression":x,"returnByValue":True})["result"]
        if "exceptionDetails" in r: return None
        return r.get("value")
    def close(self):
        try:self.ws.close()
        except:pass

US=[{"name":"lc-main","value":"en_US","url":"https://www.amazon.com/"},
    {"name":"i18n-prefs","value":"USD","url":"https://www.amazon.com/"},
    {"name":"sp-cdn","value":"L5Z9","url":"https://www.amazon.com/"},
    {"name":"session-id","value":"135-6192633-0505308","url":"https://www.amazon.com/"}]

JS="""(() => {
  const t=document.title, body=document.body?document.body.innerText:'';
  const title=document.querySelector('#productTitle')?.textContent?.trim()||'';
  const avail=document.querySelector('#availability')?.textContent?.trim()||'';
  const ar=document.querySelector('#acrPopover')?.getAttribute('title')?.trim()||null;
  const rv=document.querySelector('#acrCustomerReviewText')?.textContent?.trim()||null;
  // all onscreen prices in DOM order, take first in buybox region
  const prices=[...document.querySelectorAll('.a-price .a-offscreen')].map(e=>e.textContent.trim()).filter(x=>/\\$/.test(x));
  const uniq=[...new Set(prices)];
  const bb=document.querySelector('#corePrice_feature_div .a-price .a-offscreen')?.textContent?.trim()||null;
  const bb2=document.querySelector('#corePriceDisplay_desktop_feature_div .a-offscreen')?.textContent?.trim()||null;
  return {t,title,bb,bb2,uniq:uniq.slice(0,8),ar,rv,avail:avail.slice(0,60)};
})()"""

asin=sys.argv[1]
ws=new_tab(); cdp=CDP(ws)
cdp.call("Page.enable"); cdp.call("Runtime.enable"); cdp.call("Network.enable")
for c in US: cdp.call("Network.setCookie", c)
cdp.call("Page.navigate",{"url":f"https://www.amazon.com/dp/{asin}"})
time.sleep(12)
out=cdp.eval(JS)
print(json.dumps(out,indent=1))
cdp.close()