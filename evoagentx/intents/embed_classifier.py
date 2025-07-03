"""
Embedding-based intent classification for EvoAgentX Obsidian integration.

This module provides automatic classification between 'ask' and 'agent' modes
using OpenAI text embeddings and cosine similarity comparison against
prototype examples.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any

import httpx
import numpy as np


class Intent(str, Enum):
    """Intent classification types."""
    ASK = "ask"
    AGENT = "agent"


@dataclass
class IntentResult:
    """Result of intent classification."""
    intent: Intent
    confidence: float  # 0.0-1.0 cosine similarity


@dataclass
class IntentDebug(IntentResult):
    """Extended intent result with debugging information."""
    top_example: str
    example_score: float


# Cache configuration
CACHE_DIR = Path(".cache")
CACHE_FILE = CACHE_DIR / "intent_vectors.json"

# Prototype training examples
AGENT_EXAMPLES = [
    "generate a plan for my week",
    "create a task list",
    "schedule my meetings",
    "refactor this text",
    "build a project outline",
]

ASK_EXAMPLES = [
    "what is a project outline",
    "explain this concept",
    "summarize this paragraph",
    "define intent detection",
    "how does this work",
]

# OpenAI Configuration
OPENAI_API_URL = "https://api.openai.com/v1/embeddings"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536


class EmbeddingCache:
    """Manages the embedding cache for prototype examples."""
    
    def __init__(self):
        self.cache_data: Dict[str, Any] = {}
        self._examples_hash = self._compute_examples_hash()
        
    def _compute_examples_hash(self) -> str:
        """Compute SHA256 hash of all prototype examples."""
        all_examples = AGENT_EXAMPLES + ASK_EXAMPLES
        combined = "".join(sorted(all_examples))
        return hashlib.sha256(combined.encode()).hexdigest()
    
    async def load_or_create_cache(self) -> Dict[str, np.ndarray]:
        """
        Load cached embeddings or create new ones if cache is invalid.
        
        Returns:
            Dictionary mapping example text to embedding vectors
        """
        if await self._is_cache_valid():
            return await self._load_cache()
        else:
            return await self._create_cache()
    
    async def _is_cache_valid(self) -> bool:
        """Check if the cache exists and matches current examples."""
        if not CACHE_FILE.exists():
            return False
            
        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
            return cache_data.get("examples_hash") == self._examples_hash
        except (json.JSONDecodeError, KeyError):
            return False
    
    async def _load_cache(self) -> Dict[str, np.ndarray]:
        """Load embeddings from cache file."""
        with open(CACHE_FILE, 'r') as f:
            cache_data = json.load(f)
        
        embeddings = {}
        for text, embedding_list in cache_data["embeddings"].items():
            embeddings[text] = np.array(embedding_list, dtype=np.float32)
        
        return embeddings
    
    async def _create_cache(self) -> Dict[str, np.ndarray]:
        """Create new cache by embedding all prototype examples."""
        # Ensure cache directory exists
        CACHE_DIR.mkdir(exist_ok=True)
        
        # Get embeddings for all examples
        all_examples = AGENT_EXAMPLES + ASK_EXAMPLES
        embeddings = await self._embed_texts(all_examples)
        
        # Prepare cache data
        cache_data = {
            "examples_hash": self._examples_hash,
            "embeddings": {}
        }
        
        for text, embedding in zip(all_examples, embeddings):
            cache_data["embeddings"][text] = embedding.tolist()
        
        # Save to cache file
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        # Return as dictionary
        return {text: emb for text, emb in zip(all_examples, embeddings)}
    
    async def _embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """
        Embed a list of texts using OpenAI API.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors as numpy arrays
        """
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable is required but not set. "
                "Please set it in your environment or .env file."
            )
        
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": texts,
            "model": EMBEDDING_MODEL
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(OPENAI_API_URL, headers=headers, json=payload)
            
            if response.status_code != 200:
                error_text = response.text
                raise RuntimeError(
                    f"OpenAI API request failed with status {response.status_code}: {error_text}"
                )
            
            result = response.json()
            
            if "data" not in result:
                raise RuntimeError(f"Unexpected OpenAI API response format: {result}")
            
            embeddings = []
            for item in result["data"]:
                embedding = np.array(item["embedding"], dtype=np.float32)
                embeddings.append(embedding)
            
            return embeddings


class IntentClassifier:
    """Embedding-based intent classifier."""
    
    def __init__(self):
        self.cache = EmbeddingCache()
        self.prototype_embeddings: Dict[str, np.ndarray] = {}
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Ensure the classifier is initialized with prototype embeddings."""
        if not self._initialized:
            self.prototype_embeddings = await self.cache.load_or_create_cache()
            self._initialized = True
    
    async def classify_intent(self, text: str) -> IntentResult:
        """
        Classify the intent of input text.
        
        Args:
            text: Input text to classify
            
        Returns:
            IntentResult with classified intent and confidence score
        """
        await self._ensure_initialized()
        
        # Get embedding for input text
        input_embedding = await self._embed_single_text(text)
        
        # Calculate similarities to all prototypes
        agent_similarities = []
        ask_similarities = []
        
        for example_text, example_embedding in self.prototype_embeddings.items():
            similarity = self._cosine_similarity(input_embedding, example_embedding)
            
            if example_text in AGENT_EXAMPLES:
                agent_similarities.append(similarity)
            else:
                ask_similarities.append(similarity)
        
        # Use average similarity per class as the decision metric
        avg_agent_sim = np.mean(agent_similarities) if agent_similarities else 0.0
        avg_ask_sim = np.mean(ask_similarities) if ask_similarities else 0.0
        
        # Choose intent with higher average similarity
        if avg_agent_sim > avg_ask_sim:
            intent = Intent.AGENT
            confidence = float(avg_agent_sim)
        else:
            intent = Intent.ASK
            confidence = float(avg_ask_sim)
        
        return IntentResult(intent=intent, confidence=confidence)
    
    async def explain_intent(self, text: str) -> IntentDebug:
        """
        Classify intent with additional debugging information.
        
        Args:
            text: Input text to classify
            
        Returns:
            IntentDebug with classification result and best matching example
        """
        await self._ensure_initialized()
        
        # Get basic classification
        result = await self.classify_intent(text)
        
        # Find the best matching individual example
        input_embedding = await self._embed_single_text(text)
        
        best_example = ""
        best_score = -1.0
        
        for example_text, example_embedding in self.prototype_embeddings.items():
            similarity = self._cosine_similarity(input_embedding, example_embedding)
            if similarity > best_score:
                best_score = similarity
                best_example = example_text
        
        return IntentDebug(
            intent=result.intent,
            confidence=result.confidence,
            top_example=best_example,
            example_score=float(best_score)
        )
    
    async def _embed_single_text(self, text: str) -> np.ndarray:
        """Embed a single text string using OpenAI API."""
        embeddings = await self.cache._embed_texts([text])
        return embeddings[0]
    
    def _cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(dot_product / (norm_a * norm_b))


# Global classifier instance
_classifier = IntentClassifier()


async def classify_intent(text: str) -> IntentResult:
    """
    Classify the intent of input text as either 'ask' or 'agent' mode.
    
    Uses cosine similarity against pre-embedded prototype examples to determine
    whether the input is a question/query (ask mode) or an action/task (agent mode).
    
    Args:
        text: The input text to classify
        
    Returns:
        IntentResult containing the predicted intent and confidence score
        
    Raises:
        RuntimeError: If OPENAI_API_KEY is not set or API call fails
    """
    return await _classifier.classify_intent(text)


async def explain_intent(text: str) -> IntentDebug:
    """
    Classify intent with additional debugging information.
    
    Provides the same classification as classify_intent() but includes
    the best matching prototype example and its similarity score for
    debugging and development purposes.
    
    Args:
        text: The input text to classify
        
    Returns:
        IntentDebug containing classification result and debugging info
        
    Raises:
        RuntimeError: If OPENAI_API_KEY is not set or API call fails
    """
    return await _classifier.explain_intent(text)


# TODO: Accept `/agent {prompt}` prefix to force classification
# TODO: Local embedding fallback (sentence-transformers) when ENV `EAX_LOCAL_EMBEDDINGS=true`
# TODO: Online learning: persist user-corrected labels to cache and re-rank examples
