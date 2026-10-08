#!/bin/bash
fetch(){ curl -s --max-time 60 "https://r.jina.ai/https://www.amazon.com/s?k=$2" -o "s_$1.md"; echo "$1 $(wc -c < s_$1.md)"; }
fetch ares70030 "ARES+70030+oil+filter+cap+wrench+set"
fetch astro6070 "Astro+Pneumatic+6070"
fetch abnwrench "ABN+oil+filter+wrench+3+jaw"
fetch perfband "Performance+Tool+W173C+oil+filter+wrench"
fetch lisle63600 "Lisle+63600"
