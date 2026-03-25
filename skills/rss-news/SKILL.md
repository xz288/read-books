---
name: rss-news
description: "Fetch and parse RSS/Atom news feeds from any public URL using curl and python."
---

# RSS/News Skill

Fetch headlines and summaries from any RSS or Atom feed using curl + python. No API key needed.

## Fetch headlines from any RSS feed (titles only, max 5)

```bash
curl -s "FEED_URL" | python -c "import sys,re; items=re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>',sys.stdin.read()); [print(f'{i+1}. {a or b}') for i,(a,b) in enumerate(items[1:6])]"
```

**Important:** Output titles only — no descriptions, no raw XML. Keep output short to avoid context overflow.

## Popular Feed URLs

| Source | Feed URL |
|--------|----------|
| BBC World | `https://feeds.bbci.co.uk/news/world/rss.xml` |
| BBC Tech | `https://feeds.bbci.co.uk/news/technology/rss.xml` |
| Hacker News (top) | `https://hnrss.org/frontpage` |
| Reddit r/programming | `https://www.reddit.com/r/programming/.rss` |
| The Verge | `https://www.theverge.com/rss/index.xml` |
| Ars Technica | `https://feeds.arstechnica.com/arstechnica/index` |
| GitHub Trending | `https://github.com/trending` (not RSS — use web search instead) |

## Tips

- Replace `FEED_URL` with any RSS/Atom URL
- User can ask "latest tech news" → use Hacker News or The Verge feed
- User can ask "latest world news" → use BBC World feed
- Store user's preferred feeds in TOOLS.md for quick access
