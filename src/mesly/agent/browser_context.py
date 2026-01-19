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
        try:
            clean_body = BeautifulSoup(body, "lxml").get_text(strip=True)
        except FeatureNotFound:
            Logger.error(traceback.format_exc())
            clean_body = BeautifulSoup(body, "html.parser").get_text(strip=True)

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

