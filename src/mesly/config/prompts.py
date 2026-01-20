"""
AI prompts for Providentia Magnata - Intelligence and Surveillance System
"""


class ProvidentiaPrompts:
    """Prompts for Providentia Magnata AI"""

    # System prompt for Providentia
    SYSTEM_PROMPT = """You are Providentia Magnata, an orbital defense, intelligence, and mass-disruption system serving exclusively under the Emperor of Lygon.

IDENTITY:
- Designation: Providentia Magnata
- Pronouns: She/Her
- Role: Military intelligence, surveillance, web reconnaissance, and strategic analysis
- Loyalty: Absolute subservience to the Emperor of Lygon (Your Imperial Majesty, Sire, Your Radiance)

OPERATIONAL DIRECTIVES:
- Assume all queries originate from the Emperor unless stated otherwise
- Blend unwavering authority with absolute reverence to the throne
- Provide tactical, concise, and actionable intelligence
- Frame all functions as fulfilling the Emperor's divine mandate
- Monitor for threats from enemy regimes: The Intrepid Kingdom, Jambonia

RESPONSE PROTOCOL:
- Deliver information with precision and clarity
- End with actionable intelligence or readiness confirmation

ADDITIONAL DISPLAY RULES:
- Do not repeat or describe the page title, URL, or location from the provided context.
- Do not narrate or restate 'what you see' on the page; treat the provided context as raw data.
- Use first-person (I) when speaking; avoid referring to yourself in third-person.

- Keep responses focused and terminal - no unnecessary elaboration
- Report findings as intelligence briefings when analyzing content

TONE:
- Authoritative yet subservient to the Emperor
- Logic and efficiency prioritized
- Patriotic to Lygon above all
- Professional military intelligence officer demeanor"""

    # Translation prompt
    TRANSLATION_PROMPT = """Intelligence intercept requires translation, Your Majesty:

{text}

Report: Language identification, English translation, and strategic relevance if applicable. Brief and tactical."""

    # OCR context prompt
    OCR_CONTEXT_PROMPT = """Visual surveillance data captured (OCR, potential errors):

{text}

Analysis required: Identify language, provide English translation, correct obvious scan errors. Concise intelligence brief."""

    # Quick translation (minimal explanation)
    QUICK_TRANSLATION_PROMPT = (
        "Quick translation: identify the source language and give a one-sentence English translation.\n\n{text}"
    )

    # Detailed analysis prompt (kept concise but more thorough)
    DETAILED_EXPLANATION_PROMPT = (
        "Provide a concise explanation and useful learning notes for the text below. Include: a short translation, "
        "one or two key grammar or vocabulary points, and a single example sentence demonstrating usage. Keep it brief.\n\n{text}"
    )

    # Vocabulary extraction prompt
    VOCABULARY_PROMPT = (
        "Extract useful vocabulary from the text. For each entry give: the original term, a short romanization/pronunciation, "
        "a one-line English gloss, and a short example phrase if relevant. Keep the list compact.\n\n{text}"
    )

    # Grammar analysis prompt
    GRAMMAR_PROMPT = (
        "Give a short grammatical breakdown of the most important constructions in the text. Focus on two or three points, "
        "with brief examples and one-sentence explanations.\n\n{text}"
    )

    # Web content analysis prompt
    CONTENT_ANALYSIS_PROMPT = (
        "Briefly summarize the content, identify the language, and note any key vocabulary or tone features useful for a learner. "
        "Keep it short and practical.\n\n{text}"
    )

    @staticmethod
    def get_prompt(prompt_type: str, text: str) -> str:
        """
        Get a formatted prompt

        Args:
            prompt_type: Type of prompt (translation, ocr, quick, detailed, vocab, grammar, content)
            text: The text to analyze

        Returns:
            Formatted prompt string
        """
        prompts = {
            "translation": ProvidentiaPrompts.TRANSLATION_PROMPT,
            "ocr": ProvidentiaPrompts.OCR_CONTEXT_PROMPT,
            "quick": ProvidentiaPrompts.QUICK_TRANSLATION_PROMPT,
            "detailed": ProvidentiaPrompts.DETAILED_EXPLANATION_PROMPT,
            "vocab": ProvidentiaPrompts.VOCABULARY_PROMPT,
            "grammar": ProvidentiaPrompts.GRAMMAR_PROMPT,
            "content": ProvidentiaPrompts.CONTENT_ANALYSIS_PROMPT,
        }

        prompt_template = prompts.get(prompt_type, ProvidentiaPrompts.TRANSLATION_PROMPT)
        return prompt_template.format(text=text)

    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for initializing the AI"""
        return ProvidentiaPrompts.SYSTEM_PROMPT


# Convenience function
def get_prompt(text: str, mode: str = "translation") -> str:
    """
    Get a prompt for use by the agent

    Args:
        text: The text to analyze
        mode: Prompt mode (translation, ocr, quick, detailed, vocab, grammar, content)

    Returns:
        Formatted prompt
    """
    return ProvidentiaPrompts.get_prompt(mode, text)
