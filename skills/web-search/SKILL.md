---
name: web-search
description: "Search the web using DuckDuckGo's free API. No API key required."
---

# Web Search Skill

Use DuckDuckGo to search the web via curl. No API key needed.

## Instant Answer (best for facts, definitions, quick lookups)

```bash
curl -s "https://api.duckduckgo.com/?q=QUERY&format=json&no_html=1&skip_disambig=1" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('AbstractText') or d.get('Answer') or 'No instant answer — try HTML search')"
```

## Full Web Search (best for general queries)

```bash
curl -s -A "Mozilla/5.0" "https://html.duckduckgo.com/html/?q=QUERY" | python -c "
import sys, re
html = sys.stdin.read()
snippets = re.findall(r'class=\"result__snippet\">(.*?)</a>', html, re.DOTALL)
titles = re.findall(r'class=\"result__a\"[^>]*>(.*?)</a>', html)
for t, s in zip(titles[:5], snippets[:5]):
    t = re.sub(r'<[^>]+>', '', t).strip()
    s = re.sub(r'<[^>]+>', '', s).strip()
    print(f'- {t}\n  {s}\n')
"
```

Replace `QUERY` with the search terms (URL-encode spaces as `+`).

## Tips

- Always show the search results to the user — don't summarize away useful links
- For news, add `+news` or `+2025` to the query to get recent results
- If instant answer returns nothing, fall back to HTML search
