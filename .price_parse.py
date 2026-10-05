import re, json
txt = open('/root/garagetoolsdb/src/lib/data.mjs').read()
# Split top-level tool categories
toplevel = re.split(r'\n  "', txt)
cats = []
for t in toplevel:
    m = re.match(r'([a-z-]+)": \{\n    name: "([^"]+)"', t)
    if m:
        slug = m.group(1)
        # find product objects within this block (up to next '\n  "' top-level)
        prodblocks = re.findall(r'(\n      \{[^}]*?\})', t)
        products = []
        for pb in prodblocks:
            name = re.search(r'name: "([^"]+)"', pb)
            price = re.search(r'price: "([^"]+)"', pb)
            rating = re.search(r'rating: "([^"]+)"', pb)
            reviews = re.search(r'reviews: "([^"]+)"', pb)
            asin = re.search(r'asin: "([^"]*)"', pb)
            label = re.search(r'label: "([^"]+)"', pb)
            products.append({
                'name': name.group(1) if name else '?',
                'price': price.group(1) if price else '?',
                'rating': rating.group(1) if rating else '?',
                'reviews': reviews.group(1) if reviews else '?',
                'asin': asin.group(1) if asin else '',
                'label': label.group(1) if label else ''
            })
        cats.append({'slug': slug, 'products': products})

for c in cats:
    print(f"[{c['slug']}] {len(c['products'])} products")
    for p in c['products']:
        print(f"   - {p['name']} | {p['price']} | r={p['rating']} rev={p['reviews']} | asin={p['asin']}")
print("TOTAL:", sum(len(c['products']) for c in cats))