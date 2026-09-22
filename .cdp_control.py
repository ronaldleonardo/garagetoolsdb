#!/usr/bin/env python3
"""Control test: verify browser loads known-live OBD2 products + re-verify breaker ASINs."""
import json, time, requests, websocket
CDP_HTTP = "http://127.0.0.1:9222"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36")
def new_tab():
    r = requests.put(f"{CDP_HTTP}/json/new?about:blank", timeout=10)
    return r.json()["webSocketDebuggerUrl"]
class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=90); self.msg_id=0
    def call(self, m, p=None):
        self.msg_id+=1; mid=self.msg_id
        self.ws.send(json.dumps({"id":mid,"method":m,"params":p or {}}))
        while True:
            msg=json.loads(self.ws.recv())
            if msg.get("id")==mid:
                if "error" in msg: raise RuntimeError(f"{m}: {msg['error']}")
                return msg.get("result",{})
    def eval(self, e):
        return self.call("Runtime.evaluate",{"expression":e,"returnByValue":True})["result"]["value"]
    def close(self):
        try:self.ws.close()
        except Exception:pass
ws=new_tab(); cdp=CDP(ws)
cdp.call("Page.enable");cdp.call("Runtime.enable");cdp.call("Network.enable")
cdp.call("Network.setUserAgentOverride",{"userAgent":UA,"platform":"Win32"})
def nav(asin):
    cdp.call("Page.navigate",{"url":f"https://www.amazon.com/dp/{asin}"})
    for _ in range(10):
        time.sleep(2.5)
        v=cdp.eval("({t:document.title,body:document.body?document.body.innerText.slice(0,200):''})")
        if "Continue shopping" in v["body"]: cdp.eval("""(()=>{const b=[...document.querySelectorAll('button,a,input')].find(e=>/Continue shopping/i.test(e.textContent));if(b){b.click();return 1}return 0})()""");time.sleep(3)
        if v["body"].strip() and "Continue shopping" not in v["body"]: break
    return cdp.eval("""(()=>{const t=document.title,h=location.href,body=document.body?document.body.innerText:'';
        const sels=['#corePrice_feature_div .a-price .a-offscreen','#corePriceDisplay_desktop_feature_div .a-offscreen','span.priceToPay span.a-offscreen','#price_inside_buybox','span.a-price span.a-offscreen'];
        let price=null;for(const s of sels){const el=document.querySelector(s);if(el&&el.textContent.trim()){price=el.textContent.trim();break}}
        const dead=/Page Not Found|We couldn't find|Sorry, we just need to make sure|entered the wrong/i.test(t+body);
        return {t:t.slice(0,80),h,price,dead,body:body.slice(0,150)}})()""")
tests=[("CONTROL ANCEL OBD2","B01G5EA74I"),("CONTROL LAUNCH OBD2","B073GW5MTS"),
       ("breaker TEKTON","B07C9B7Z8W"),("breaker SK 3/4","B0002NYWQ2")]
out=[]
for name,asin in tests:
    try: out.append({"name":name,"asin":asin,**nav(asin)})
    except Exception as e: out.append({"name":name,"asin":asin,"error":str(e)})
    time.sleep(2)
cdp.close()
print(json.dumps(out,indent=2))