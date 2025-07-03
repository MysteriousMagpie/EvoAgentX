"""
Unit tests for the embedding-based intent classifier.

Tests both the core classification logic and edge cases.
"""

import pytest
import asyncio
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

import numpy as np

from evoagentx.intents import (
    classify_intent,
    explain_intent,
    Intent,
    IntentResult,
    IntentDebug,
)
from evoagentx.intents.embed_classifier import (
    EmbeddingCache,
    IntentClassifier,
    AGENT_EXAMPLES,
    ASK_EXAMPLES,
)


class TestIntentEnums:
    """Test the Intent enum."""
    
    def test_intent_values(self):
        """Test that Intent enum has correct values."""
        assert Intent.ASK == "ask"
        assert Intent.AGENT == "agent"
        assert len(Intent) == 2


class TestDataClasses:
    """Test the data classes."""
    
    def test_intent_result(self):
        """Test IntentResult creation."""
        result = IntentResult(intent=Intent.ASK, confidence=0.85)
        assert result.intent == Intent.ASK
        assert result.confidence == 0.85
    
    def test_intent_debug(self):
        """Test IntentDebug creation."""
        debug = IntentDebug(
            intent=Intent.AGENT,
            confidence=0.92,
            top_example="create a task list",
            example_score=0.88
        )
        assert debug.intent == Intent.AGENT
        assert debug.confidence == 0.92
        assert debug.top_example == "create a task list"
        assert debug.example_score == 0.88


class TestEmbeddingCache:
    """Test the embedding cache functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file = Path(self.temp_dir) / "test_vectors.json"
        
    def test_examples_hash_consistency(self):
        """Test that examples hash is consistent."""
        cache1 = EmbeddingCache()
        cache2 = EmbeddingCache()
        assert cache1._compute_examples_hash() == cache2._compute_examples_hash()
    
    def test_examples_hash_changes_with_content(self):
        """Test that hash changes when examples change."""
        cache = EmbeddingCache()
        original_hash = cache._compute_examples_hash()
        
        # Temporarily modify examples
        original_agent = AGENT_EXAMPLES[:]
        AGENT_EXAMPLES.append("new example")
        
        try:
            modified_hash = cache._compute_examples_hash()
            assert original_hash != modified_hash
        finally:
            # Restore original examples
            AGENT_EXAMPLES[:] = original_agent
    
    @pytest.mark.asyncio
    async def test_cache_invalid_when_missing(self):
        """Test that cache is invalid when file doesn't exist."""
        cache = EmbeddingCache()
        
        # Use a non-existent cache file
        with patch('evoagentx.intents.embed_classifier.CACHE_FILE', self.cache_file):
            assert not await cache._is_cache_valid()
    
    @pytest.mark.asyncio 
    async def test_cache_invalid_when_hash_mismatch(self):
        """Test that cache is invalid when hash doesn't match."""
        cache = EmbeddingCache()
        
        # Create a cache file with wrong hash
        cache_data = {
            "examples_hash": "wrong_hash",
            "embeddings": {}
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f)
        
        with patch('evoagentx.intents.embed_classifier.CACHE_FILE', self.cache_file):
            assert not await cache._is_cache_valid()
    
    @pytest.mark.asyncio
    async def test_cache_valid_when_hash_matches(self):
        """Test that cache is valid when hash matches."""
        cache = EmbeddingCache()
        correct_hash = cache._compute_examples_hash()
        
        # Create a cache file with correct hash
        cache_data = {
            "examples_hash": correct_hash,
            "embeddings": {}
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f)
        
        with patch('evoagentx.intents.embed_classifier.CACHE_FILE', self.cache_file):
            assert await cache._is_cache_valid()


class TestIntentClassifier:
    """Test the main intent classifier."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = IntentClassifier()
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        vec_a = np.array([1, 0, 0], dtype=np.float32)
        vec_b = np.array([1, 0, 0], dtype=np.float32)
        
        similarity = self.classifier._cosine_similarity(vec_a, vec_b)
        assert abs(similarity - 1.0) < 1e-6
    
    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity for orthogonal vectors."""
        vec_a = np.array([1, 0], dtype=np.float32)
        vec_b = np.array([0, 1], dtype=np.float32)
        
        similarity = self.classifier._cosine_similarity(vec_a, vec_b)
        assert abs(similarity - 0.0) < 1e-6
    
    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity with zero vector."""
        vec_a = np.array([1, 1], dtype=np.float32)
        vec_b = np.array([0, 0], dtype=np.float32)
        
        similarity = self.classifier._cosine_similarity(vec_a, vec_b)
        assert similarity == 0.0


class TestPublicFunctions:
    """Test the public API functions."""
    
    @pytest.mark.asyncio
    async def test_classify_intent_missing_api_key(self):
        """Test that classification fails when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
                await classify_intent("test message")
    
    @pytest.mark.asyncio
    async def test_explain_intent_missing_api_key(self):
        """Test that explanation fails when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
                await explain_intent("test message")
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    async def test_classify_intent_with_mocked_embeddings(self):
        """Test classification with mocked embeddings."""
        # Mock the embedding cache to return fake embeddings
        fake_embeddings = {
            # Agent examples - higher similarity to agent-like input
            "generate a plan for my week": np.array([1.0, 0.0, 0.0], dtype=np.float32),
            "create a task list": np.array([0.9, 0.1, 0.0], dtype=np.float32),
            "schedule my meetings": np.array([0.8, 0.2, 0.0], dtype=np.float32),
            "refactor this text": np.array([0.7, 0.3, 0.0], dtype=np.float32),
            "build a project outline": np.array([0.6, 0.4, 0.0], dtype=np.float32),
            
            # Ask examples - higher similarity to ask-like input
            "what is a project outline": np.array([0.0, 0.0, 1.0], dtype=np.float32),
            "explain this concept": np.array([0.1, 0.0, 0.9], dtype=np.float32),
            "summarize this paragraph": np.array([0.2, 0.0, 0.8], dtype=np.float32),
            "define intent detection": np.array([0.3, 0.0, 0.7], dtype=np.float32),
            "how does this work": np.array([0.4, 0.0, 0.6], dtype=np.float32),
        }
        
        # Mock the cache loading
        with patch.object(EmbeddingCache, 'load_or_create_cache', return_value=fake_embeddings):
            # Mock the single text embedding for agent-like input
            with patch.object(EmbeddingCache, '_embed_texts', return_value=[np.array([0.9, 0.1, 0.0], dtype=np.float32)]):
                result = await classify_intent("make me a schedule")
                
                assert isinstance(result, IntentResult)
                assert result.intent == Intent.AGENT
                assert result.confidence > 0.0
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    async def test_explain_intent_with_mocked_embeddings(self):
        """Test explanation with mocked embeddings."""
        fake_embeddings = {
            "what is a project outline": np.array([1.0, 0.0, 0.0], dtype=np.float32),
            "explain this concept": np.array([0.8, 0.2, 0.0], dtype=np.float32),
            "summarize this paragraph": np.array([0.6, 0.4, 0.0], dtype=np.float32),
            "define intent detection": np.array([0.5, 0.5, 0.0], dtype=np.float32),
            "how does this work": np.array([0.4, 0.6, 0.0], dtype=np.float32),
            "generate a plan for my week": np.array([0.0, 0.0, 1.0], dtype=np.float32),
            "create a task list": np.array([0.2, 0.0, 0.8], dtype=np.float32),
            "schedule my meetings": np.array([0.3, 0.0, 0.7], dtype=np.float32),
            "refactor this text": np.array([0.4, 0.0, 0.6], dtype=np.float32),
            "build a project outline": np.array([0.5, 0.0, 0.5], dtype=np.float32),
        }
        
        with patch.object(EmbeddingCache, 'load_or_create_cache', return_value=fake_embeddings):
            # Mock asking-like input
            with patch.object(EmbeddingCache, '_embed_texts', return_value=[np.array([0.9, 0.1, 0.0], dtype=np.float32)]):
                result = await explain_intent("what does this mean?")
                
                assert isinstance(result, IntentDebug)
                assert result.intent == Intent.ASK
                assert result.confidence > 0.0
                assert result.top_example in fake_embeddings
                assert result.example_score > 0.0


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_malformed_cache_file(self):
        """Test handling of malformed cache file."""
        temp_dir = tempfile.mkdtemp()
        cache_file = Path(temp_dir) / "bad_cache.json"
        
        # Create malformed JSON
        with open(cache_file, 'w') as f:
            f.write("invalid json content")
        
        cache = EmbeddingCache()
        
        with patch('evoagentx.intents.embed_classifier.CACHE_FILE', cache_file):
            assert not await cache._is_cache_valid()
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    async def test_openai_api_error(self):
        """Test handling of OpenAI API errors."""
        
        # Mock httpx to return an error response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            cache = EmbeddingCache()
            
            with pytest.raises(RuntimeError, match="OpenAI API request failed"):
                await cache._embed_texts(["test"])


if __name__ == "__main__":
    pytest.main([__file__])
