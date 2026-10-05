#!/usr/bin/env python3
import json, requests, websocket, time, sys

def new_tab():
    r = requests.put("http://127.0.0.1:9222/json/new?about:blank", timeout=10)
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
        r = self.call("Runtime.evaluate", {"expression": expr, "returnByValue": True})["result"]
        if "exceptionDetails" in r: return "EXC:"+str(r["exceptionDetails"].get("text",""))
        return r.get("value")
    def close(self):
        try: self.ws.close()
        except Exception: pass

ws = new_tab(); cdp = CDP(ws)
cdp.call("Page.enable"); cdp.call("Runtime.enable")
cdp.call("Page.navigate", {"url": "https://www.amazon.com/dp/B08R9B7S3T"})
time.sleep(8)
v = cdp.eval("({t:document.title, h:location.href, body:document.body?document.body.innerText.slice(0,600):''})")
print(json.dumps(v, indent=2))
cdp.close()