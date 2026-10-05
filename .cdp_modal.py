#!/usr/bin/env python3
import json, requests, websocket, time, sys, re
target = sys.argv[1]
tabs = json.loads(requests.get("http://127.0.0.1:9222/json", timeout=15).text)
tw=None
for t in tabs:
    if t.get("type")=="page" and target in t.get("url",""): tw=t["webSocketDebuggerUrl"]; break
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
# click See All Buying Options
clicked=js("""(() => { const b=[...document.querySelectorAll('button')].find(e=>/See All Buying Options/i.test(e.textContent)); if(b){b.click();return'clicked';} const a=[...document.querySelectorAll('a')].find(e=>/See All Buying Options/i.test(e.textContent)); if(a){a.click();return'clickedA';} return'notfound'; })()""")
print("click:",clicked)
time.sleep(5)
# modal now
res=js("""(() => {
  const modal=document.querySelector('#aod-content, #aod-container, .aod-container, #all-offers-display');
  const txt=modal?modal.innerText.slice(0,900):(document.body.innerText.includes('All Selling Options')||document.body.innerText.includes('aod')?document.body.innerText.match(/\\$[0-9][0-9.,]*/g):['no modal']);
  return {txt};
})()""")
print(json.dumps(res, indent=1)[:2500])
ws.close()