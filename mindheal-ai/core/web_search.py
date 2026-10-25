"""Lightweight public web search using Google Search results.

No separate search API key is required. Google may rate-limit automated requests;
if that happens, the function returns no results rather than inventing information.
"""
from html.parser import HTMLParser
from urllib.parse import quote, urlparse, parse_qs
import requests


class _GoogleResultsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self._anchor = None
        self._inside_h3 = False
        self._snippet = None
        self._snippet_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()

        if tag == "a" and attrs.get("href", "").startswith("http"):
            href = attrs["href"]
            parsed = urlparse(href)
            # Google result links can occasionally be wrapped in /url?q=...
            if parsed.path == "/url":
                href = parse_qs(parsed.query).get("q", [href])[0]
            if href.startswith("http") and "google.com" not in urlparse(href).netloc:
                self._anchor = {"title": "", "url": href, "snippet": ""}
        elif tag == "h3" and self._anchor is not None:
            self._inside_h3 = True

        if "VwiC3b" in classes or "yXK7lf" in classes:
            self._snippet = self.results[-1] if self.results else None
            self._snippet_depth = 1

    def handle_data(self, data):
        if self._inside_h3 and self._anchor is not None:
            self._anchor["title"] += data
        elif self._snippet is not None:
            self._snippet["snippet"] += data

    def handle_endtag(self, tag):
        if tag == "h3" and self._inside_h3:
            self._inside_h3 = False
        elif tag == "a" and self._anchor is not None and not self._inside_h3:
            item = self._anchor
            item["title"] = " ".join(item["title"].split())
            if item["title"] and item["url"].startswith("http"):
                if not any(x["url"] == item["url"] for x in self.results):
                    self.results.append(item)
            self._anchor = None
        if self._snippet is not None:
            if tag in ("div", "span"):
                self._snippet_depth -= 1
                if self._snippet_depth <= 0:
                    self._snippet = None


def search_web(query, max_results=5):
    """Return Google web results; network, block, and parser errors return []."""
    query = " ".join(str(query or "").split())[:500]
    if not query:
        return []
    try:
        response = requests.get(
            "https://www.google.com/search?q=" + quote(query) + "&num=" + str(max_results),
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=(3, 8),
        )
        response.raise_for_status()
        parser = _GoogleResultsParser()
        parser.feed(response.text)
        for item in parser.results:
            item["snippet"] = " ".join(item["snippet"].split())
        return parser.results[:max_results]
    except Exception:
        return []


def needs_web_search(text):
    """Automatically search factual/general queries entered in the normal chat box.

    Keep personal emotional-support conversations and short conversational follow-ups
    model-led so they are not delayed by an unnecessary network request.
    """
    value = " ".join(str(text or "").lower().split())
    if not value:
        return False

    # Explicit current/live intents always trigger a web lookup.
    live_terms = (
        "latest", "breaking news", "headlines", "news today", "today's news",
        "gold rate", "gold price", "silver rate", "silver price", "bitcoin price",
        "crypto price", "stock price", "share price", "market rate", "current rate",
        "price today", "rates today", "rate today", "today rate", "today's rate",
        "exchange rate", "usd to pkr", "pkr to usd", "currency rate",
        "petrol price", "fuel price", "current price", "right now", "live score",
        "weather today", "weather in", "forecast today", "latest update",
        "current president", "current prime minister", "today in pakistan",
    )
    if any(term in value for term in live_terms):
        return True

    support_phrases = (
        "i feel ", "i am feeling", "i'm feeling", "i feel like",
        "i am sad", "i'm sad", "i am lonely", "i'm lonely",
        "i feel lonely", "i feel sad", "i feel anxious", "i feel scared",
        "i am afraid", "i'm afraid", "i regret", "i was rejected",
        "my relationship", "my family", "my friend hates", "i need someone",
        "i just want to talk", "can i talk", "help me calm down",
        "i am stressed", "i'm stressed", "i feel overwhelmed",
    )
    if any(phrase in value for phrase in support_phrases):
        return False

    follow_ups = (
        "why?", "why", "how so?", "how so", "tell me more", "explain more",
        "what about it?", "what about it", "and then?", "and then",
        "what do you mean?", "what do you mean", "any other tip", "any other tips",
        "any more tips", "anything else", "what else", "another tip", "more advice",
        "can you elaborate", "go on", "continue",
    )
    if value in follow_ups or any(
        value.startswith(prefix) for prefix in (
            "any other tip", "any other tips", "any more tips", "anything else",
            "what else", "another tip", "more advice", "can you elaborate",
        )
    ):
        return False

    return True


def clean_search_query(text):
    """Remove chat-command prefixes before sending a query to the search engine."""
    value = " ".join(str(text or "").split())
    for prefix in ("/search", "search:", "web:"):
        if value.lower().startswith(prefix):
            return value[len(prefix):].strip()
    return value
