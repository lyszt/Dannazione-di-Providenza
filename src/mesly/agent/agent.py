from typing import Deque, Dict, Optional, Union
import json
from transformers import pipeline
import io
import numpy as np
from scipy.io.wavfile import write

from src.mesly import Logger
from src.mesly.agent.browser_context import BrowserContext
from src.mesly.agent.memory.short_term import ShortTermMemory
from src.mesly.agent.memory.long_term import LongTermMemory
from src.mesly.agent.self_identity import SelfIdentity
from src.mesly.config import ConfigTemplate, SystemSpecs
from src.mesly.config.gpuconfig import GPUConfig
from src.mesly.config.prompts import ProvidentiaPrompts, get_prompt
from src.mesly.llm import LLMClientManager, LocalLLMClientManager
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]


class KnowledgeBase:
    def __init__(self, config):
        self.browser_context: BrowserContext = BrowserContext()
        self.config = config

    def to_dict(self) -> dict:
        """Convert knowledge base to JSON-serializable dict"""
        return {
            "browser_context": {
                "recent_pages": len(self.browser_context.get_context()),
                "selected_text": self.browser_context.selected_text[:100] if self.browser_context.selected_text else None
            },
            "config_provider": self.config.ai.preferred_provider if self.config else None
        }


class Agent:
    def __init__(self, config: ConfigTemplate, specs: SystemSpecs = None):
        """
        Initialize Agent with AI client based on configuration

        Args:
            config: Configuration template containing AI provider settings
            specs: Optional SystemSpecs for feature gating. Created internally if not provided.
        """
        self.tts_ref_codes = None
        self.tts_engine = None
        self.config = config
        self.specs = specs if specs is not None else SystemSpecs()

        # Initialize GPU configuration - check compatibility on boot
        self.gpu_config = self.specs.gpu_config

        # Conditionally initialize NeuTTS based on config and specs
        neutts_enabled = getattr(config.performance, "neutts_enabled", True)
        min_ram = getattr(config.performance, "min_ram_neutts_gb", 8.0)
        max_swap = getattr(config.performance, "max_swap_used_gb", 6.0)
        if neutts_enabled and self.specs.supports_neutts(
            min_ram_gb=min_ram, max_swap_used_gb=max_swap
        ):
            try:
                sys.path.insert(0, str(ROOT / "vendor" / "neutts"))
                from neutts import NeuTTS
                self.tts_engine = NeuTTS(
                    backbone_repo="neuphonic/neutts-nano-q8-gguf",
                    backbone_device="cpu",
                    codec_repo="neuphonic/neucodec",
                    codec_device="cpu",
                )
                Logger.info("Agent: NeuTTS initialized")
            except Exception as e:
                Logger.warning(f"Agent: NeuTTS init failed ({e}), audio synthesis disabled")
                self.tts_engine = None
        else:
            reason = []
            if self.specs.ram_available_gb < min_ram:
                reason.append(f"need {min_ram}GB available RAM (have {self.specs.ram_available_gb:.1f}GB)")
            if self.specs.swap_used_gb > max_swap:
                reason.append(f"swap pressure too high ({self.specs.swap_used_gb:.1f}GB used, max {max_swap}GB)")
            path = self.specs._get_neutts_vendor_path()
            if not path or not path.exists():
                reason.append("vendor/neutts missing")
            Logger.warning(f"Agent: NeuTTS disabled ({'; '.join(reason)})")

        self.knowledge_base = KnowledgeBase(config)
        self.profile = SelfIdentity()
        self.profile.available_tools = []
        self.profile.active_context = json.dumps(self.knowledge_base.to_dict())
        self.short_term_memory = ShortTermMemory()
        
        # Initialize long-term memory
        try:
            self.long_term_memory = LongTermMemory()
            Logger.info("Agent: Long-term memory initialized")
        except Exception as e:
            Logger.error(f"Agent: Failed to initialize long-term memory: {e}")
            self.long_term_memory = None
        self.ai_client: Optional[Union[LLMClientManager, LocalLLMClientManager]] = None

        # Initialize sentiment analyzer with correct device
        device_id = 0 if self.gpu_config.is_gpu_available() else -1  # -1 means CPU for transformers
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=device_id
        )

        # Initialize AI client based on preferred provider
        self._initialize_ai_client()

    def _initialize_ai_client(self) -> None:
        """Initialize AI client based on config preferred provider"""
        preferred_provider = self.config.ai.preferred_provider

        if preferred_provider in ["gemini", "openai"]:
            # Cloud AI providers
            try:
                self.ai_client = LLMClientManager(provider=preferred_provider, settings=self.config)
                if self.ai_client.is_available():
                    Logger.info(f"Agent: {preferred_provider.capitalize()} client initialized")
                else:
                    Logger.warning(f"Agent: {preferred_provider} client not available")
                    self.ai_client = None
            except Exception as e:
                Logger.error(f"Agent: Failed to initialize {preferred_provider} client: {e}")
                self.ai_client = None

        elif preferred_provider in ["ollama", "llamacpp"]:
            # Local LLM providers - check specs before init
            min_ram = getattr(self.config.performance, "min_ram_local_llm_gb", 4.0)
            if not self.specs.supports_local_llm(min_ram_gb=min_ram):
                Logger.warning(
                    f"Agent: Local LLM disabled (need {min_ram}GB available RAM, "
                    f"have {self.specs.ram_available_gb:.1f}GB)"
                )
                self.ai_client = None
            else:
                try:
                    self.ai_client = LocalLLMClientManager(provider=preferred_provider, settings=self.config)
                    if self.ai_client.is_available():
                        Logger.info(f"Agent: {preferred_provider.capitalize()} client initialized")
                    else:
                        Logger.warning(f"Agent: {preferred_provider} client not available")
                        self.ai_client = None
                except Exception as e:
                    Logger.error(f"Agent: Failed to initialize {preferred_provider} client: {e}")
                    self.ai_client = None
        else:
            Logger.error(f"Agent: Unknown provider '{preferred_provider}'")
            self.ai_client = None

    def is_ready(self) -> bool:
        """Check if agent has a working AI client"""
        return self.ai_client is not None and self.ai_client.is_available()

    def generate(self, prompt: str, system_prompt: Optional[str] = None, stream_callback=None) -> Optional[str]:
        """
        Generate text response using the agent's AI client

        Args:
            prompt: User prompt/question
            system_prompt: Optional system instructions
            stream_callback: Optional callback function for streaming (receives text chunks)

        Returns:
            Generated text or None if failed
        """
        if not self.is_ready():
            Logger.error("Agent: AI client not available for generation")
            return None

        try:
            response = self.ai_client.generate(prompt, system_prompt, stream_callback)
            # Save conversation to long-term memory
            if response and self.long_term_memory:
                try:
                    self.long_term_memory.conversations.save(
                    user_input=prompt,
                    ai_response=response,
                    context_type="simple"
                    )
                    Logger.debug("Agent: Conversation saved to long-term memory")
                except Exception as e:
                    Logger.error(f"Agent: Failed to save conversation to long-term memory: {e}")
            return response
        except Exception as e:
            Logger.error(f"Agent: Generation failed: {e}")
            return None

    def generate_with_context(self, prompt: str, system_prompt: Optional[str] = None,
                             use_browser_context: bool = True,
                             use_memory_context: bool = True,
                             stream_callback=None) -> Optional[str]:
        """
        Generate text with agent's knowledge base context

        Args:
            prompt: User prompt/question
            system_prompt: Optional system instructions
            use_browser_context: Include browser context in prompt
            use_memory_context: Include short-term memory context (high activation memories)
            stream_callback: Optional callback for streaming

        Returns:
            Generated text or None if failed
        """
        if not self.is_ready():
            Logger.error("Agent: AI client not available for generation")
            return None

        # Prune old/low-activation memories before generating
        self.short_term_memory.prune()

        # Build context-enriched prompt
        enriched_prompt = ""

        # Add memory context if requested (most emotionally salient interactions)
        if use_memory_context:
            memory_summary = self.short_term_memory.get_context_summary()
            if memory_summary and memory_summary != "No recent memories.":
                enriched_prompt += f"{memory_summary}\n\n"
                Logger.debug("Agent: Including high-activation memories in context")

        # Add browser context if requested
        if use_browser_context and self.knowledge_base.browser_context.get_context():
            context_str = self._format_browser_context()
            enriched_prompt += f"{context_str}\n\n"

        # Add user prompt
        enriched_prompt += f"User question: {prompt}"

        return self.generate(enriched_prompt, system_prompt, stream_callback)

    def _format_browser_context(self) -> str:
        """Format browser context for inclusion in prompts"""
        contexts = self.knowledge_base.browser_context.get_context()

        if not contexts:
            return ""

        formatted = "Recent browser context:\n"
        for i, ctx in enumerate(contexts, 1):
            formatted += f"\n[Page {i}]\n"
            formatted += f"Title: {ctx.get('title', 'Unknown')}\n"
            formatted += f"URL: {ctx.get('url', 'Unknown')}\n"
            body_content = ctx.get('body', '')
            # Include up to 3000 characters to capture full news articles
            formatted += f"Content: {body_content[:3000]}{'...' if len(body_content) > 3000 else ''}\n"

        return formatted

    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment of text to inform agent reactions

        Args:
            text: Text to analyze

        Returns:
            Sentiment analysis result with label and score
        """
        try:
            result = self.sentiment_analyzer(text[:512])[0]  # Truncate to model limit
            Logger.debug(f"Agent: Sentiment - {result['label']} ({result['score']:.2f})")
            return result
        except Exception as e:
            Logger.error(f"Agent: Sentiment analysis failed: {e}")
            return {"label": "NEUTRAL", "score": 0.5}

    def process_ocr_text(self, ocr_text: str, mode: str = "ocr",
                        system_prompt: Optional[str] = None, stream_callback=None) -> Optional[str]:
        """
        Process OCR-extracted text with intelligence analysis

        Args:
            ocr_text: Text extracted from OCR
            mode: Type of OCR processing ("ocr", "translation", "explanation")
            system_prompt: Optional custom system prompt
            stream_callback: Optional streaming callback

        Returns:
            AI response or None if failed
        """
        if not self.is_ready():
            Logger.error("Agent: Cannot process OCR text, AI client not ready")
            return None

        # Analyze sentiment to understand user's emotional state
        sentiment = self.analyze_sentiment(ocr_text)

        # Use default Providentia system prompt if not provided
        if system_prompt is None:
            system_prompt = ProvidentiaPrompts.get_system_prompt()

        # Build the user prompt based on mode
        user_prompt = get_prompt(ocr_text, mode=mode)

        Logger.info(f"Agent: Processing OCR text (mode={mode}, {len(ocr_text)} chars, sentiment={sentiment['label']})")

        # Add to short-term memory
        self.short_term_memory.add_item({
            "type": "ocr_processing",
            "mode": mode,
            "text": ocr_text[:200],
            "sentiment": sentiment,
            "timestamp": "now"
        })

        return self.generate(user_prompt, system_prompt, stream_callback)

    def synthesize_audio(self, text: str) -> Optional[tuple[str, bytes]]:
        """
        Synthesize text to audio using NeuTTS.

        Returns a tuple (mime_type, audio_bytes) or None on failure.
        """
        if not text or self.tts_engine is None:
            return None

        try:
            ref_audio_path = ROOT / "src" / "assets" / "voice_ref.wav"

            if not ref_audio_path.exists():
                Logger.warning(f"Agent: Reference audio not found at {ref_audio_path}. Cannot synthesize.")
                return None

            if not hasattr(self, "tts_ref_codes") or self.tts_ref_codes is None:
                Logger.info(f"Agent: Encoding reference audio from {ref_audio_path}")
                self.tts_ref_codes = self.tts_engine.encode_reference(str(ref_audio_path))

            ref_text = "The quick brown fox jumps over the lazy dog."
            audio_array = self.tts_engine.infer(text, self.tts_ref_codes, ref_text)

            if audio_array is None or len(audio_array) == 0:
                Logger.warning("Agent: Audio synthesis returned empty waveform")
                return None



            # Convert float32 [-1, 1] to int16 PCM
            audio_int16 = (audio_array * 32767).astype(np.int16)

            byte_io = io.BytesIO()
            # NeuTTS uses 24kHz sample rate
            write(byte_io, 24000, audio_int16)
            audio_bytes = byte_io.getvalue()

            Logger.info("Agent: Audio synthesized successfully")
            return "audio/wav", audio_bytes

        except Exception as e:
            Logger.error(f"Agent: Audio synthesis failed: {e}")
            return None

    def process_user_question(self, question: str, context_text: Optional[str] = None,
                             system_prompt: Optional[str] = None,
                             use_browser_context: bool = False,
                             stream_callback=None) -> Optional[str]:
        """
        Process a direct user question with optional context

        Args:
            question: User's question
            context_text: Optional context text (e.g., OCR text, document snippet)
            system_prompt: Optional system prompt
            use_browser_context: Whether to include browser context
            stream_callback: Optional streaming callback

        Returns:
            AI response or None if failed
        """
        if not self.is_ready():
            Logger.error("Agent: Cannot process question, AI client not ready")
            return None

        # Analyze sentiment of question to gauge user's tone
        sentiment = self.analyze_sentiment(question)

        # Use default Providentia system prompt if not provided
        if system_prompt is None:
            system_prompt = ProvidentiaPrompts.get_system_prompt()

        # Build enriched prompt
        enriched_prompt = ""

        # Add conversation history from short-term memory
        memory_summary = self.short_term_memory.get_context_summary()
        if memory_summary and memory_summary != "No recent memories.":
            enriched_prompt += f"Conversation history:\n{memory_summary}\n\n"
            Logger.debug("Agent: Including conversation history in context")

        # Add browser context if requested
        if use_browser_context and self.knowledge_base.browser_context.get_context():
            enriched_prompt += self._format_browser_context() + "\n\n"

        # Add context text if provided
        if context_text:
            enriched_prompt += f"Context text:\n{context_text}\n\n"

        # Add user question
        enriched_prompt += f"User question: {question}"

        Logger.info(f"Agent: Processing user question: '{question[:50]}...' (sentiment={sentiment['label']})")

        # Generate response
        response = self.generate(enriched_prompt, system_prompt, stream_callback)

        # Add to short-term memory with response
        self.short_term_memory.add_item({
            "type": "user_question",
            "question": question,
            "response": response[:200] if response else None,
            "has_context": context_text is not None,
            "sentiment": sentiment,
            "timestamp": "now"
        })

        return response

    def process_screenshot_inquiry(self, ocr_text: str, user_question: str,
                                   system_prompt: Optional[str] = None,
                                   stream_callback=None) -> Optional[str]:
        """
        Process user inquiry about a screenshot with OCR text

        Args:
            ocr_text: Text extracted from screenshot
            user_question: User's question about the screenshot
            system_prompt: Optional system prompt
            stream_callback: Optional streaming callback

        Returns:
            AI response or None if failed
        """
        if not self.is_ready():
            Logger.error("Agent: Cannot process screenshot inquiry, AI client not ready")
            return None

        # Analyze sentiment of both OCR text and user question
        ocr_sentiment = self.analyze_sentiment(ocr_text)
        question_sentiment = self.analyze_sentiment(user_question)

        # Use default Providentia system prompt if not provided
        if system_prompt is None:
            system_prompt = ProvidentiaPrompts.get_system_prompt()

        # Build combined prompt
        combined_prompt = f"""This text was extracted from a screenshot:

        {ocr_text}
        
        User's question: {user_question}
        
        Answer briefly and clearly."""

        Logger.info(f"Agent: Processing screenshot inquiry - OCR: {len(ocr_text)} chars, Question: '{user_question[:50]}...'")
        Logger.debug(f"Agent: OCR sentiment={ocr_sentiment['label']}, Question sentiment={question_sentiment['label']}")

        # Add to short-term memory
        self.short_term_memory.add_item({
            "type": "screenshot_inquiry",
            "ocr_text": ocr_text[:200],
            "question": user_question,
            "ocr_sentiment": ocr_sentiment,
            "question_sentiment": question_sentiment,
            "timestamp": "now"
        })

        return self.generate(combined_prompt, system_prompt, stream_callback)

    def log_memory_state(self):
        """Log current memory activation states for debugging"""
        Logger.info(f"Short-Term Memory State: {len(self.short_term_memory.active.items)} memories")

        if not self.short_term_memory.active.items:
            Logger.info("No memories stored")
            return

        sorted_memories = sorted(
            self.short_term_memory.active.items,
            key=lambda x: x.activation,
            reverse=True
        )

        for i, mem in enumerate(sorted_memories, 1):
            content = mem.content
            mem_type = content.get('type', 'unknown')
            Logger.info(f"[{i}] {mem_type} | Activation: {mem.activation:.2f} | Boost: {mem.sentiment_boost:.1f}")

            if 'sentiment' in content:
                sent = content['sentiment']
                Logger.debug(f"    Sentiment: {sent.get('label')} ({sent.get('score', 0):.2f})")

            if mem_type == 'screenshot_inquiry':
                Logger.debug(f"    Q: {content.get('question', '')[:60]}...")
            elif mem_type == 'user_question':
                Logger.debug(f"    Q: {content.get('question', '')[:60]}...")

    def close(self):
        """Close agent resources including long-term memory database connection"""
        if self.long_term_memory:
            try:
                self.long_term_memory.close()
                Logger.info("Agent: Long-term memory closed")
            except Exception as e:
                Logger.error(f"Agent: Failed to close long-term memory: {e}")

    def cleanup_old_memories(self, conversation_days: int = 30, browser_days: int = 7):
        """
        Cleanup old data from long-term memory

        Args:
            conversation_days: Delete conversations older than this many days
            browser_days: Delete browser history older than this many days
        """
        if not self.long_term_memory:
            Logger.warning("Agent: Cannot cleanup memories, long-term memory not initialized")
            return

        try:
            conv_deleted = self.long_term_memory.conversations.delete_old(days=conversation_days)
            browser_deleted = self.long_term_memory.browser_history.delete_old(days=browser_days)

            Logger.info(f"Agent: Cleaned up {conv_deleted} old conversations and {browser_deleted} browser history entries")
        except Exception as e:
            Logger.error(f"Agent: Failed to cleanup old memories: {e}")

    def get_memory_stats(self) -> Optional[Dict]:
        """Get statistics about the agent's long-term memory"""
        if not self.long_term_memory:
            return None

        try:
            return self.long_term_memory.get_stats()
        except Exception as e:
            Logger.error(f"Agent: Failed to get memory stats: {e}")
            return None
