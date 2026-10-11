"""Lightweight web search for current/public information.

Uses DuckDuckGo's HTML results page; no API key is required. Search is only
called for requests that clearly need online information.
"""
from html.parser import HTMLParser
from urllib.parse import quote
import requests


class _ResultsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self._current = None
        self._capture = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "")
        if tag == "a" and "result__a" in classes:
            self._current = {
                "title": "",
                "url": attrs.get("href", ""),
                "snippet": "",
            }
            self._capture = "title"
        elif self._current is not None and tag in ("a", "div", "span") and (
            "result__snippet" in classes
        ):
            self._capture = "snippet"

    def handle_data(self, data):
        if self._current is not None and self._capture in ("title", "snippet"):
            self._current[self._capture] += data

    def handle_endtag(self, tag):
        if self._current is None:
            return
        if tag == "a" and self._capture == "title":
            self._capture = None
        if tag == "div" and self._capture == "snippet":
            self._capture = None
        if self._current and self._current["title"].strip() and self._current["url"].startswith("http"):
            self._current["title"] = " ".join(self._current["title"].split())
            self._current["snippet"] = " ".join(self._current["snippet"].split())
            if not any(x["url"] == self._current["url"] for x in self.results):
                self.results.append(self._current)
            self._current = None
            self._capture = None


def search_web(query, max_results=5):
    """Return a list of public web results; errors safely return an empty list."""
    query = " ".join(str(query or "").split())[:300]
    if not query:
        return []
    try:
        response = requests.get(
            "https://html.duckduckgo.com/html/?q=" + quote(query),
            headers={"User-Agent": "Mozilla/5.0 (compatible; MindHealAI/1.0)"},
            timeout=8,
        )
        response.raise_for_status()
        parser = _ResultsParser()
        parser.feed(response.text)
        return parser.results[:max_results]
    except Exception:
        return []


def needs_web_search(text):
    """Conservative intent check: only search when the user asks for online facts."""
    value = str(text or "").lower()
    phrases = (
        "search the web", "search online", "look online", "find online",
        "on the internet", "from the internet", "latest news", "current news",
        "latest research", "recent research", "current information",
        "look up", "find sources", "give me sources", "website for",
        "song lyrics", "lyrics of", "lyrics for", "find lyrics",
        "who won today", "today's news", "today news", "recent update",
        "latest update", "current price", "as of today",
    )
    return any(p in value for p in phrases)
