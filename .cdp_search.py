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
        r = self.call("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})["result"]
        if "exceptionDetails" in r: return {"__exc__": str(r["exceptionDetails"].get("text",""))}
        return r.get("value")
    def close(self):
        try: self.ws.close()
        except Exception: pass

SEARCH_JS = """(() => {
    const cards = [...document.querySelectorAll('div[data-component-type="s-search-result"]')];
    return cards.slice(0,6).map(c => {
        const aid = c.getAttribute('data-asin');
        const h2a = c.querySelector('h2 a');
        const title = h2a ? (h2a.getAttribute('title') || h2a.textContent?.trim() || '') : (c.querySelector('h2')?.textContent?.trim() || '');
        // price
        const whole = c.querySelector('span.a-price > span.a-offscreen, .a-price .a-offscreen');
        const price = whole ? whole.textContent.trim() : '';
        // rating + reviews
        const ar = c.querySelector('span.a-icon-alt')?.textContent?.trim() || '';
        const rv = c.querySelector('span.a-size-base.s-underline-text, a[aria-label]')?.textContent?.trim() || '';
        const revAnchor = c.querySelector('div[data-cy="reviews-block"] span.a-size-base, span[aria-label*="ratings"]');
        const link = c.querySelector('h2 a')?.getAttribute('href') || '';
        return {asin: aid, title, price, ar, rv, link};
    }).filter(x => x.asin);
})()"""

US_COOKIES = [
    {"name":"lc-main","value":"en_US","url":"https://www.amazon.com/"},
    {"name":"i18n-prefs","value":"USD","url":"https://www.amazon.com/"},
    {"name":"sp-cdn","value":"L5Z9","url":"https://www.amazon.com/"},
    {"name":"session-id","value":"135-6192633-0505308","url":"https://www.amazon.com/"},
]

def search(q):
    cdp.call("Page.enable"); cdp.call("Runtime.enable")
    cdp.call("Network.enable")
    for c in US_COOKIES:
        cdp.call("Network.setCookie", c)
    url = "https://www.amazon.com/s?k=" + urllib.parse.quote(q)
    cdp.call("Page.navigate", {"url": url})
    for _ in range(10):
        time.sleep(2.5)
        v = cdp.eval("({t:document.title, body:document.body?document.body.innerText.slice(0,200):''})")
        if "robot" in v["t"]+v["body"] or "Continue shopping" in v["body"]:
            cdp.eval("""(() => { const b=[...document.querySelectorAll('button,a')].find(e=>/Continue shopping/i.test(e.textContent)); if(b){b.click(); return 'clk';} return 'nf'; })()""")
            time.sleep(2)
        if not v["t"].startswith("Page Not Found") and v["body"].strip():
            break
    return cdp.eval(SEARCH_JS)

if __name__ == "__main__":
    queries = json.loads(sys.argv[1])
    ws = new_tab(); cdp = CDP(ws)
    out = []
    for q in queries:
        try:
            out.append({"q": q, "results": search(q)})
        except Exception as e:
            out.append({"q": q, "error": str(e)})
        time.sleep(1)
    cdp.close()
    print(json.dumps(out, indent=2))