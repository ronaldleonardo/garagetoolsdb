#!/usr/bin/env python3
import json, requests, websocket, time, sys
target = sys.argv[1]
tabs = json.loads(requests.get("http://127.0.0.1:9222/json", timeout=15).text)
tw=None; cur=None
for t in tabs:
    if t.get("type")=="page" and target in t.get("url",""): tw=t["webSocketDebuggerUrl"]; cur=t["url"]; break
if not tw: print(json.dumps({"error":"no tab"})); sys.exit(1)
ws=websocket.create_connection(tw,timeout=90); nid=1
def call(m,p=None):
    global nid; i=nid; nid+=1
    ws.send(json.dumps({"id":i,"method":m,"params":p or {}}))
    while True:
        msg=json.loads(ws.recv())
        if msg.get("id")==i:
            if "error" in msg: raise RuntimeError(f"{m}: {msg['error']}")
            return msg.get("result",{})
def js(x):
    r=call("Runtime.evaluate",{"expression":x,"returnByValue":True})["result"]
    if "exceptionDetails" in r: return None
    return r.get("value")
time.sleep(4)
res=js("""(() => {
  const t=document.title, h=location.href, body=document.body?document.body.innerText:'';
  const prices=[...document.querySelectorAll('.a-price .a-offscreen')].map(e=>e.textContent.trim()).filter(x=>/\\$/.test(x));
  return {t, h, prices:[...new Set(prices)].slice(0,10), body_head:body.slice(0,200)};
})()""")
print(json.dumps(res, indent=1))
ws.close()