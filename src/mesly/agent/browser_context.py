import traceback
from typing import List, Dict, Deque
from collections import deque
from bs4 import BeautifulSoup, FeatureNotFound

from ..utils import Logger, HotkeyManager


class BrowserContext:
    def __init__(self, max_len: int = 3):
        self.context: Deque[Dict[str, str]] = deque(maxlen=max_len)
        self.selected_text: str = ""

    def push(self, url: str, title: str, body: str) -> None:
        soup = BeautifulSoup(body, "lxml")

        # Remove script, style, and other non-readable elements
        for element in soup(['script', 'style', 'noscript', 'iframe', 'svg', 'path', 'nav', 'header', 'footer']):
            element.decompose()

        # Extract all readable text
        clean_body = soup.get_text(strip=True, separator=' ')

        # Clean up multiple spaces and newlines
        clean_body = ' '.join(clean_body.split())

        Logger.debug(f"Browser context: Added page '{title}' with {len(clean_body)} chars of content")

        self.context.append({
            "url": url,
            "title": title,
            "body": clean_body
        })

    def pop(self) -> Dict[str, str]:
        """Pop the most recent page agent from the stack"""
        if self.context:
            return self.context.pop()
        return {}

    def get_context(self) -> List[Dict[str, str]]:
        """Get the current browser agent as a list"""
        return list(self.context)

