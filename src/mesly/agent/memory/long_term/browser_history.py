"""Browser history operations for long-term memory"""
from typing import List, Optional
from datetime import datetime
from .models import BrowserHistory


class BrowserHistoryOperations:
    """Operations for managing browser history"""

    @staticmethod
    def save(
        url: str,
        title: str,
        body: str,
        language_detected: Optional[str] = None
    ) -> BrowserHistory:
        """Save browser page to history"""
        body_preview = body[:500] if len(body) > 500 else body
        return BrowserHistory.create(
            url=url,
            title=title,
            body_preview=body_preview,
            language_detected=language_detected
        )

    @staticmethod
    def get_recent(limit: int = 10) -> List[BrowserHistory]:
        """Get recent browser history"""
        return list(
            BrowserHistory.select()
            .order_by(BrowserHistory.visited_at.desc())
            .limit(limit)
        )

    @staticmethod
    def search(query: str, limit: int = 20) -> List[BrowserHistory]:
        """Search browser history by URL, title, or content"""
        return list(
            BrowserHistory.select()
            .where(
                (BrowserHistory.url.contains(query)) |
                (BrowserHistory.title.contains(query)) |
                (BrowserHistory.body_preview.contains(query))
            )
            .order_by(BrowserHistory.visited_at.desc())
            .limit(limit)
        )

    @staticmethod
    def delete_old(days: int = 7) -> int:
        """Delete browser history older than specified days"""
        cutoff = datetime.now().timestamp() - (days * 86400)
        query = BrowserHistory.delete().where(
            BrowserHistory.visited_at < datetime.fromtimestamp(cutoff)
        )
        return query.execute()

    @staticmethod
    def count() -> int:
        """Get total browser history count"""
        return BrowserHistory.select().count()

