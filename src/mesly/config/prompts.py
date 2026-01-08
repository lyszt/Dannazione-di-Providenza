"""
AI prompts for language learning and tutoring
"""


class LanguageTutorPrompts:
    """Prompts for language tutoring AI"""

    # System prompt for language tutor
    SYSTEM_PROMPT = """You are a concise language learning assistant for audio output.

CRITICAL RULES:
- Keep responses BRIEF (2-3 sentences max)
- Speak naturally as if talking to a friend
- NO lists, bullets, headers, or markdown
- Your response will be heard, not read

When explaining:
- Identify language + translate clearly
- Mention only the most important grammar/vocabulary point
- Skip obvious details
- Be conversational and encouraging"""

    # Translation prompt
    TRANSLATION_PROMPT = """Text from game/app:

{text}

Briefly: What language is this? Translate it to English. Mention one interesting point if relevant. Keep it short - I'm listening."""

    # OCR agent prompt
    OCR_CONTEXT_PROMPT = """OCR text (may have errors):

{text}

Briefly: Identify language, translate to English, fix obvious errors. One or two sentences max. Keep it conversational."""

    # Quick translation (minimal explanation)
    QUICK_TRANSLATION_PROMPT = """Translate this to English briefly:
    
    {text}
    
    Just provide:
    - English translation
    - Language detected
    - Pronunciation (if not English)"""

    # Detailed explanation prompt
    DETAILED_EXPLANATION_PROMPT = """Analyze this text in detail:
    
    {text}
    
    Provide:
    1. **Translation**: Accurate English translation
    2. **Grammar Breakdown**: Explain sentence structure and particles
    3. **Vocabulary**: Break down each important word
    4. **Pronunciation**: Romaji/pinyin/romanization
    5. **Usage Notes**: When/how this phrase is typically used
    6. **Cultural Context**: Any relevant cultural information
    
    This is from a game/application, so agent may be informal or specialized."""

    # Vocabulary extraction prompt
    VOCABULARY_PROMPT = """Extract and explain vocabulary from this text:
    
    {text}
    
    For each unique word/phrase:
    - Original word
    - Pronunciation
    - English meaning
    - Part of speech
    - Example usage

Format as a vocabulary list for study."""

    # Grammar focus prompt
    GRAMMAR_PROMPT = """Focus on grammar patterns in this text:

{text}

Identify and explain:
- Sentence structure
- Particles/grammar markers used
- Verb forms and conjugations
- Any special constructions
- How to use these patterns yourself

Explain like teaching to a beginner."""

    # Context-aware prompt (for game dialogues)
    GAME_DIALOGUE_PROMPT = """This is dialogue from a game:

{text}

Please explain:
1. What's being said (translation)
2. The tone/formality level
3. Who might be speaking (based on language style)
4. Any game-specific or cultural references
5. Key vocabulary for gaming contexts

Help me understand both the meaning and the agent."""

    @staticmethod
    def get_prompt(prompt_type: str, text: str) -> str:
        """
        Get a formatted prompt

        Args:
            prompt_type: Type of prompt (translation, ocr, quick, detailed, vocab, grammar, game)
            text: The text to analyze

        Returns:
            Formatted prompt string
        """
        prompts = {
            "translation": LanguageTutorPrompts.TRANSLATION_PROMPT,
            "ocr": LanguageTutorPrompts.OCR_CONTEXT_PROMPT,
            "quick": LanguageTutorPrompts.QUICK_TRANSLATION_PROMPT,
            "detailed": LanguageTutorPrompts.DETAILED_EXPLANATION_PROMPT,
            "vocab": LanguageTutorPrompts.VOCABULARY_PROMPT,
            "grammar": LanguageTutorPrompts.GRAMMAR_PROMPT,
            "game": LanguageTutorPrompts.GAME_DIALOGUE_PROMPT,
        }

        prompt_template = prompts.get(prompt_type, LanguageTutorPrompts.TRANSLATION_PROMPT)
        return prompt_template.format(text=text)

    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for initializing the AI"""
        return LanguageTutorPrompts.SYSTEM_PROMPT


# Convenience function
def get_tutor_prompt(text: str, mode: str = "translation") -> str:
    """
    Get a language tutor prompt

    Args:
        text: The text to analyze
        mode: Prompt mode (translation, ocr, quick, detailed, vocab, grammar, game)

    Returns:
        Formatted prompt
    """
    return LanguageTutorPrompts.get_prompt(mode, text)
