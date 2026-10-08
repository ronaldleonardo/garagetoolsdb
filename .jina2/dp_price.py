import re, sys, json, subprocess, time

def fetch(asin):
    url = f"https://r.jina.ai/https://www.amazon.com/dp/{asin}"
    p = subprocess.run(["curl", "-s", "--max-time", "70", url], capture_output=True, text=True)
    return p.stdout

def price_of(md):
    m = re.search(r'desktop_buybox_group_1":\[\{"displayPrice":"\$([\d,]+\.\d{2})"', md)
    if m: return m.group(1), 'buybox'
    m = re.search(r'Price\nSubtotal\n\$\$([\d,]+\.\d{2})', md)
    if m: return m.group(1), 'price-subtotal'
    m = re.search(r'displayPrice":"\$([\d,]+\.\d{2})"', md)
    if m: return m.group(1), 'any-buybox'
    return '', 'none'

for asin in sys.argv[1:]:
    md = fetch(asin)
    pr, how = price_of(md)
    t = re.search(r'Title: (.+)', md)
    title = (t.group(1).strip() if t else '')[:90]
    open(f"/root/garagetoolsdb/.jina2/dp_{asin}.md","w").write(md)
    print(f"{asin}  ${pr:>8} [{how}]  {title}")
    time.sleep(1)
