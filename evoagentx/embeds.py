"""
Utility functions for embeddings in EvoAgentX.
"""

from typing import List
from evoagentx.intents.embed_classifier import EmbeddingCache


async def get_embedding(text: str) -> List[float]:
    """
    Get embedding for a single text string.
    
    Args:
        text: The text to embed
        
    Returns:
        List of float values representing the embedding vector
    """
    # Create a cache instance to reuse the embedding functionality
    cache = EmbeddingCache()
    
    # Use the private _embed_texts method to get embeddings
    embeddings = await cache._embed_texts([text])
    
    # Return the first (and only) embedding as a list
    return embeddings[0].tolist()
