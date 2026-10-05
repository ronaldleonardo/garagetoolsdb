#!/usr/bin/env python3
import json, requests, websocket, sys
target = sys.argv[1]
tabs = json.loads(requests.get("http://127.0.0.1:9222/json", timeout=15).text)
tw=None
for t in tabs:
    if t.get("type")=="page" and target in t.get("url",""): tw=t["webSocketDebuggerUrl"]; break
if not tw: print(json.dumps({"error":"no tab"})); sys.exit(1)
ws=websocket.create_connection(tw,timeout=60); nid=1
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
# Dump the buybox/center text block + any 'See all buying options'
JS="""(() => {
  const cc=document.querySelector('#centerCol, #corePrice_feature_div, #buybox');
  const txt=cc?cc.innerText.slice(0,400):'(no center)';
  const hasOol=/see all buying options|aod|offers/i.test(document.body.innerText);
  const buyboxDiv=document.querySelector('#buybox')?.innerText?.slice(0,300)||'';
  // price inside an offer/olp context
  const olp=document.querySelector('#priceMatch_feature_div, #offer_feature_div, .olp')?.innerText?.slice(0,200)||'';
  return {txt, buyboxDiv, hasOol, olp};
})()"""
print(json.dumps(js(JS), indent=1))
ws.close()