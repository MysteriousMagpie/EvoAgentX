"""
Intent classification module for EvoAgentX.

Provides embedding-based classification between 'ask' and 'agent' modes
for automatic mode switching in the Obsidian integration.
"""

from .embed_classifier import (
    Intent,
    IntentResult,
    IntentDebug,
    classify_intent,
    explain_intent,
)

__all__ = [
    "Intent",
    "IntentResult", 
    "IntentDebug",
    "classify_intent",
    "explain_intent",
]
