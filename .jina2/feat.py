import re, sys
for a in sys.argv[1:]:
    md = open(f"/root/garagetoolsdb/.jina2/dp_{a}.md", encoding='utf-8', errors='replace').read()
    print(f"===== {a} =====")
    m = re.search(r'About this item(.{0,1500})', md, re.S)
    if m:
        seg = m.group(1)
        # bullets often look like "*   text" or lines after
        lines = [l.strip(' *\t') for l in seg.split('\n') if l.strip().startswith('*')]
        for l in lines[:8]:
            print("  -", l[:110])
    # title
    t = re.search(r'Title: (.+)', md)
    print("  TITLE:", (t.group(1) if t else '')[:120])
