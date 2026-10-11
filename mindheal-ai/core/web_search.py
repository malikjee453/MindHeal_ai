"""Lightweight web search for current/public information.

Uses DuckDuckGo's HTML results page; no API key is required.
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
        self._snippet_target = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "")
        if tag == "a" and "result__a" in classes:
            self._current = {"title": "", "url": attrs.get("href", ""), "snippet": ""}
            self._capture = "title"
        elif "result__snippet" in classes and self.results:
            self._snippet_target = self.results[-1]
            self._capture = "snippet"

    def handle_data(self, data):
        if self._capture == "title" and self._current is not None:
            self._current["title"] += data
        elif self._capture == "snippet" and self._snippet_target is not None:
            self._snippet_target["snippet"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self._capture == "title" and self._current is not None:
            item = self._current
            item["title"] = " ".join(item["title"].split())
            item["url"] = item["url"].strip()
            if item["title"] and item["url"].startswith("http"):
                if not any(x["url"] == item["url"] for x in self.results):
                    self.results.append(item)
            self._current = None
            self._capture = None
        elif self._capture == "snippet" and tag in ("a", "div", "span"):
            self._capture = None
            self._snippet_target = None


def search_web(query, max_results=5):
    """Return public web results; errors safely return an empty list."""
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
        for item in parser.results:
            item["snippet"] = " ".join(item["snippet"].split())
        return parser.results[:max_results]
    except Exception:
        return []


def needs_web_search(text):
    """Search only when the user clearly asks for online/current information."""
    value = str(text or "").lower()
    phrases = (
        "search the web", "search online", "look online", "find online",
        "on the internet", "from the internet", "latest news", "current news",
        "latest research", "recent research", "current information",
        "look up", "find sources", "give me sources", "website for",
        "song lyrics", "lyrics of", "lyrics for", "find lyrics", "lyric of",
        "who won today", "today's news", "today news", "recent update",
        "latest update", "current price", "as of today",
    )
    return any(phrase in value for phrase in phrases)
