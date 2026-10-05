#!/usr/bin/env python3
import json, requests, websocket, time, sys
# attach to existing tab matching URL substring, eval extraction
target = sys.argv[1]  # url substring
tabs = json.loads(requests.get("http://127.0.0.1:9222/json", timeout=15).text)
tw = None
for t in tabs:
    if t.get("type")=="page" and target in t.get("url",""):
        tw = t["webSocketDebuggerUrl"]; break
if not tw:
    print(json.dumps({"error":"no tab for "+target})); sys.exit(1)
ws = websocket.create_connection(tw, timeout=60); nid=1
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
JS="""(() => {
  const t=document.title;
  const title=document.querySelector('#productTitle')?.textContent?.trim()||'';
  const bb=document.querySelector('#corePrice_feature_div .a-price .a-offscreen')?.textContent?.trim()||null;
  const bb2=document.querySelector('#corePriceDisplay_desktop_feature_div .a-offscreen')?.textContent?.trim()||null;
  const ar=document.querySelector('#acrPopover')?.getAttribute('title')?.trim()||null;
  const rv=document.querySelector('#acrCustomerReviewText')?.textContent?.trim()||null;
  const avail=document.querySelector('#availability')?.textContent?.trim()||'';
  const prices=[...new Set([...document.querySelectorAll('.a-price .a-offscreen')].map(e=>e.textContent.trim()).filter(x=>/\\$/.test(x)))];
  return {t,title,bb,bb2,ar,rv,avail:avail.slice(0,50),prices:prices.slice(0,8)};
})()"""
print(json.dumps(js(JS), indent=1))
ws.close()