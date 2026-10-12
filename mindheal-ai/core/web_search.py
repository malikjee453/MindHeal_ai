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


def search_web(query, max_results=3):
    """Return public web results; errors safely return an empty list."""
    query = " ".join(str(query or "").split())[:300]
    if not query:
        return []
    try:
        response = requests.get(
            "https://html.duckduckgo.com/html/?q=" + quote(query),
            headers={"User-Agent": "Mozilla/5.0 (compatible; MindHealAI/1.0)"},
            timeout=3,
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
    """Automatically search factual/general queries entered in the normal chat box.

    Keep personal emotional-support conversations and short conversational follow-ups
    model-led so they are not delayed by an unnecessary network request.
    """
    value = " ".join(str(text or "").lower().split())
    if not value:
        return False

    # Personal-support statements should remain conversational, not trigger web search.
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

    # Only obvious conversational follow-ups skip search; short factual queries
    # such as "who is Einstein" should still search the web.
    follow_ups = (
        "why?", "why", "how so?", "how so", "tell me more", "explain more",
        "what about it?", "what about it", "and then?", "and then",
        "what do you mean?", "what do you mean",
    )
    if value in follow_ups:
        return False

    # Explicit commands are searchable; other substantive prompts default to
    # online lookup so the same chat box works as a general search chatbot.
    return True


def clean_search_query(text):
    """Remove chat-command prefixes before sending a query to the search engine."""
    value = " ".join(str(text or "").split())
    for prefix in ("/search", "search:", "web:"):
        if value.lower().startswith(prefix):
            return value[len(prefix):].strip()
    return value
