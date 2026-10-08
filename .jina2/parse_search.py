import re, sys, json

def parse(path):
    md = open(path, encoding='utf-8', errors='replace').read()
    # find blocks: heading with product link
    # pattern: ## [title](https://www.amazon.com/<slug>/dp/<ASIN>/...)
    items = []
    for m in re.finditer(r'##\s*\[(.+?)\]\(https://www\.amazon\.com/[^)\s]*?/dp/([A-Z0-9]{10})', md):
        title = m.group(1).strip()
        asin = m.group(2)
        seg = md[m.end():m.end()+2500]
        pm = re.search(r'Price, product page\[\$([\d,]+\.\d{2})', seg)
        price = pm.group(1) if pm else ''
        items.append({'title': title, 'asin': asin, 'price': price})
    # dedupe by asin keeping first
    seen = set(); out = []
    for it in items:
        if it['asin'] in seen: continue
        seen.add(it['asin']); out.append(it)
    return out

if __name__ == '__main__':
    path = sys.argv[1]
    kw = [k.lower() for k in sys.argv[2:]]
    for it in parse(path):
        t = it['title'].lower()
        hit = all(k in t for k in kw) if kw else True
        flag = 'MATCH' if hit else '     '
        print(f"{flag} {it['asin']}  ${it['price']:>8}  {it['title'][:95]}")
