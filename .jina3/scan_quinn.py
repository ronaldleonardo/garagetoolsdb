import re
p = '/root/garagetoolsdb/.jina3/s_quinn.md'
txt = open(p, encoding='utf-8', errors='ignore').read()
print("len", len(txt))
for b in ["TEKTON", "GEARWRENCH", "DEWALT", "CRAFTSMAN", "NEIKO", "CASOMAN", "QUINN", "Pittsburgh",
          "No results", "did not match", "Amazon's Choice"]:
    print(f"{b}: {txt.count(b)}")
print("counts:", re.findall(r'[\d,]+ results? for[^\n]{0,60}', txt)[:3])
print("nores:", re.findall(r'No results for[^\n]{0,80}', txt)[:3])
