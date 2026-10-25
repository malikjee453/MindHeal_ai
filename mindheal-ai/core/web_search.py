"""Google Search HTML adapter for public live-web lookups.

Google can rate-limit automated requests. The caller must treat an empty result list
as a search failure and must never fabricate current facts.
"""
from html.parser import HTMLParser
from urllib.parse import quote, urlparse, parse_qs
import requests


class _GoogleResultsParser(HTMLParser):
    """Parse result links by their h3 headings, tolerating relative Google redirect URLs."""
    def __init__(self):
        super().__init__()
        self.results = []
        self.anchor = None
        self.in_h3 = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            href = attrs.get("href", "")
            target = ""
            if href.startswith("/url?"):
                target = parse_qs(urlparse(href).query).get("q", [""])[0]
            elif href.startswith("http://") or href.startswith("https://"):
                target = href
            if target.startswith(("http://", "https://")):
                host = urlparse(target).netloc.lower()
                if not (host == "google.com" or host.endswith(".google.com")):
                    self.anchor = {"title": "", "url": target, "has_heading": False}
        elif tag == "h3" and self.anchor is not None:
            self.in_h3 = True
            self.anchor["has_heading"] = True

    def handle_data(self, data):
        if self.in_h3 and self.anchor is not None:
            self.anchor["title"] += data

    def handle_endtag(self, tag):
        if tag == "h3":
            self.in_h3 = False
        elif tag == "a" and self.anchor is not None and not self.in_h3:
            item = self.anchor
            item["title"] = " ".join(item["title"].split())
            if item["has_heading"] and item["title"] and item["url"]:
                if not any(existing["url"] == item["url"] for existing in self.results):
                    self.results.append({
                        "title": item["title"],
                        "url": item["url"],
                        "snippet": "",
                    })
            self.anchor = None


def search_web(query, max_results=5):
    """Fetch Google search results; return [] if blocked or no parseable results."""
    query = " ".join(str(query or "").split())[:500]
    if not query:
        return []
    try:
        response = requests.get(
            "https://www.google.com/search",
            params={"q": query, "num": max(1, min(int(max_results), 10)), "hl": "en", "gl": "pk"},
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-PK,en;q=0.9",
            },
            timeout=(4, 10),
        )
        response.raise_for_status()
        parser = _GoogleResultsParser()
        parser.feed(response.text)
        return parser.results[:max_results]
    except Exception:
        return []


def needs_web_search(text):
    """Search factual/current queries while keeping emotional support conversational."""
    value = " ".join(str(text or "").lower().split())
    if not value:
        return False
    live_terms = (
        "latest", "breaking news", "headlines", "news today", "today's news",
        "gold rate", "gold price", "gold rates", "gold prices", "sone ka rate",
        "sona rate", "سونے کا ریٹ", "سونے کی قیمت", "silver rate", "silver price",
        "bitcoin price", "crypto price", "stock price", "share price", "market rate",
        "current rate", "price today", "rates today", "rate today", "today rate",
        "today's rate", "exchange rate", "usd to pkr", "pkr to usd", "currency rate",
        "dollar rate", "dollar price", "petrol price", "fuel price", "current price",
        "right now", "live score", "weather today", "weather in", "forecast today",
        "latest update", "current president", "current prime minister", "today in pakistan",
    )
    if any(term in value for term in live_terms):
        return True

    support_phrases = (
        "i feel ", "i am feeling", "i'm feeling", "i feel like", "i am sad", "i'm sad",
        "i am lonely", "i'm lonely", "i feel lonely", "i feel sad", "i feel anxious",
        "i feel scared", "i am afraid", "i'm afraid", "i regret", "i was rejected",
        "my relationship", "my family", "my friend hates", "i need someone",
        "i just want to talk", "can i talk", "help me calm down", "i am stressed",
        "i'm stressed", "i feel overwhelmed",
    )
    if any(phrase in value for phrase in support_phrases):
        return False

    follow_ups = (
        "why?", "why", "how so?", "how so", "tell me more", "explain more",
        "what about it?", "what about it", "and then?", "and then", "what do you mean?",
        "what do you mean", "any other tip", "any other tips", "any more tips",
        "anything else", "what else", "another tip", "more advice", "can you elaborate",
        "go on", "continue",
    )
    if value in follow_ups or any(value.startswith(prefix) for prefix in (
        "any other tip", "any other tips", "any more tips", "anything else",
        "what else", "another tip", "more advice", "can you elaborate",
    )):
        return False
    return True


def clean_search_query(text):
    """Remove chat-command prefixes before sending a query to Google."""
    value = " ".join(str(text or "").split())
    for prefix in ("/search", "search:", "web:"):
        if value.lower().startswith(prefix):
            return value[len(prefix):].strip()
    return value
