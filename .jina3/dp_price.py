import re, sys, json, subprocess, time, os

OUT = "/root/garagetoolsdb/.jina3"
os.makedirs(OUT, exist_ok=True)

def fetch(asin):
    url = f"https://r.jina.ai/https://www.amazon.com/dp/{asin}"
    p = subprocess.run(["curl", "-s", "--max-time", "90", url], capture_output=True, text=True)
    return p.stdout

def price_of(md):
    m = re.search(r'desktop_buybox_group_1":\[\{"displayPrice":"\$([\d,]+\.\d{2})"', md)
    if m: return m.group(1), 'buybox'
    m = re.search(r'Price\nSubtotal\n\$\$([\d,]+\.\d{2})', md)
    if m: return m.group(1), 'price-subtotal'
    m = re.search(r'displayPrice":"\$([\d,]+\.\d{2})"', md)
    if m: return m.group(1), 'any-buybox'
    return '', 'none'

def rating_reviews(md):
    r = re.search(r'([\d.]+) out of 5 stars', md)
    v = re.search(r'([\d,]+) ratings', md)
    return (r.group(1) if r else ''), (v.group(1) if v else '')

for asin in sys.argv[1:]:
    md = fetch(asin)
    pr, how = price_of(md)
    t = re.search(r'Title: (.+)', md)
    title = (t.group(1).strip() if t else '')[:110]
    rt, rv = rating_reviews(md)
    oos = "Currently unavailable" in md
    open(f"{OUT}/dp_{asin}.md", "w").write(md)
    print(f"{asin}  ${pr:>9} [{how}]  r={rt} rev={rv} oos={oos}")
    print(f"    TITLE: {title}")
    time.sleep(1)
