#!/bin/bash
fetch(){ curl -s --max-time 60 "https://r.jina.ai/https://www.amazon.com/s?k=$2" -o "s_$1.md"; echo "$1 $(wc -c < s_$1.md)"; }
fetch brandares "ARES+oil+filter"
fetch brandastro "Astro+Pneumatic+oil+filter+pliers"
fetch brandabn "ABN+oil+filter+wrench"
