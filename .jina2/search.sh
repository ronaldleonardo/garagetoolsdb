#!/bin/bash
declare -A Q=(
 [ares]="ARES+17+piece+oil+filter+cap+wrench+set+70030"
 [astro]="Astro+Pneumatic+6070+oil+filter+pliers"
 [lisle]="Lisle+63600+oil+filter+wrench+3%2F8+drive"
 [abn]="ABN+universal+3+jaw+oil+filter+wrench"
 [perf]="Performance+Tool+oil+filter+band+wrench+W173C"
)
for k in "${!Q[@]}"; do
  curl -s --max-time 60 "https://r.jina.ai/https://www.amazon.com/s?k=${Q[$k]}" -o ".jina2/s_${k}.md"
  echo "$k $(wc -c < .jina2/s_${k}.md)"
done
