from typing import Dict, Deque, List, Any, Tuple
from uuid import UUID
from collections import deque
from dataclasses import dataclass, field
import time


@dataclass
class MemoryItem:
    """Individual memory item with activation tracking"""
    content: Dict[str, Any]
    activation: float = 1.0  # Base activation level
    timestamp: float = field(default_factory=time.time)
    sentiment_boost: float = 0.0  # Emotional intensity boost


@dataclass
class ActiveSTM:
    score: float
    items: deque[MemoryItem]


class ShortTermMemory:
    def __init__(self, decay_rate=0.1, max_memories=10):
        self.memory: Dict[UUID, Deque] = {}
        self.decay_rate = decay_rate
        self.max_memories = max_memories
        self.active: ActiveSTM = ActiveSTM(score=1.0, items=deque(maxlen=max_memories))

    def _calculate_sentiment_boost(self, sentiment: Dict[str, Any]) -> float:
        """
        Calculate activation boost based on sentiment extremity

        Extreme emotions (very positive or very negative) increase memory salience

        Args:
            sentiment: Dict with 'label' and 'score' from sentiment analyzer

        Returns:
            Boost multiplier (0.0 to 2.0)
        """
        if not sentiment:
            return 0.0

        score = sentiment.get('score', 0.5)
        label = sentiment.get('label', 'NEUTRAL')

        # High confidence in emotion = more extreme = higher boost
        if label in ['POSITIVE', 'NEGATIVE']:
            # Score close to 1.0 means very confident in the emotion
            if score > 0.85:
                return 2.0  # Very extreme emotion, double activation
            elif score > 0.75:
                return 1.5  # Strong emotion
            elif score > 0.65:
                return 1.0  # Moderate emotion
            else:
                return 0.5  # Mild emotion

        return 0.0  # Neutral has no boost

    def add_item(self, item_content: Dict[str, Any]):
        """
        Add item to short-term memory with sentiment-based activation

        Args:
            item_content: Dict containing memory data, may include 'sentiment' key
        """
        # Extract sentiment if present
        sentiment = item_content.get('sentiment', None)
        sentiment_boost = self._calculate_sentiment_boost(sentiment)

        # Calculate initial activation (base + sentiment boost)
        initial_activation = 1.0 + sentiment_boost

        # Create memory item
        memory_item = MemoryItem(
            content=item_content,
            activation=initial_activation,
            timestamp=time.time(),
            sentiment_boost=sentiment_boost
        )

        self.active.items.append(memory_item)

    def get_most_activated(self, n: int = 3) -> List[MemoryItem]:
        """
        Get the N most activated memories

        Args:
            n: Number of top memories to retrieve

        Returns:
            List of MemoryItem objects sorted by activation (highest first)
        """
        sorted_items = sorted(
            self.active.items,
            key=lambda x: x.activation,
            reverse=True
        )
        return sorted_items[:n]

    def decay_activations(self):
        """
        Apply decay to all memory activations based on age

        Memories fade over time, but emotional memories fade slower
        """
        now = time.time()
        for item in self.active.items:
            age = now - item.timestamp

            # Emotional memories resist decay better
            effective_decay = self.decay_rate / (1 + item.sentiment_boost * 0.3)

            # Apply decay
            decay_factor = 1 - (age * effective_decay)
            item.activation = max(0.1, item.activation * decay_factor)

    def prune(self, activation_threshold: float = 0.2):
        """
        Remove memories below activation threshold

        Args:
            activation_threshold: Minimum activation to keep in memory
        """
        self.decay_activations()

        # Remove low-activation items
        items_to_keep = deque(maxlen=self.max_memories)
        for item in self.active.items:
            if item.activation >= activation_threshold:
                items_to_keep.append(item)

        self.active.items = items_to_keep

    def get_context_summary(self) -> str:
        """
        Get a summary of the most important memories for context

        Returns:
            Formatted string of top activated memories
        """
        top_memories = self.get_most_activated(n=3)

        if not top_memories:
            return "No recent memories."

        summary = "Recent important interactions:\n"
        for i, mem in enumerate(top_memories, 1):
            content = mem.content
            mem_type = content.get('type', 'unknown')
            activation = mem.activation
            summary += f"{i}. [{mem_type}] (activation: {activation:.2f})\n"

            if mem_type == 'screenshot_inquiry':
                summary += f"   Question: {content.get('question', '')[:50]}...\n"
            elif mem_type == 'user_question':
                summary += f"   Question: {content.get('question', '')[:50]}...\n"
            elif mem_type == 'ocr_processing':
                summary += f"   Mode: {content.get('mode', 'unknown')}\n"

        return summary
