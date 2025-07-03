"""
Test script for the embedding-based intent classifier.

This script demonstrates the usage of the intent classification module
and can be run to verify the implementation works correctly.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from evoagentx.intents import classify_intent, explain_intent, Intent


async def test_intent_classifier():
    """Test the intent classifier with sample inputs."""
    
    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found. Please set it in your environment or .env file.")
        return
    
    print("🧠 Testing EvoAgentX Intent Classifier")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        # Should classify as ASK
        "What is machine learning?",
        "Can you explain this concept to me?",
        "How does this algorithm work?",
        "Define artificial intelligence",
        
        # Should classify as AGENT  
        "Create a project plan for next week",
        "Generate a todo list for my tasks",
        "Build an outline for my presentation",
        "Refactor this code snippet",
        "Schedule my meetings for tomorrow",
    ]
    
    print("Testing classification (classify_intent):")
    print("-" * 40)
    
    for text in test_cases:
        try:
            result = await classify_intent(text)
            print(f"Input: '{text}'")
            print(f"  → Intent: {result.intent.value.upper()}")
            print(f"  → Confidence: {result.confidence:.3f}")
            print()
        except Exception as e:
            print(f"❌ Error classifying '{text}': {e}")
            print()
    
    print("\nTesting explanation (explain_intent):")
    print("-" * 40)
    
    # Test with a few examples using explain_intent
    explain_cases = [
        "What is the purpose of this function?",  # Should be ASK
        "Generate documentation for this module",  # Should be AGENT
    ]
    
    for text in explain_cases:
        try:
            result = await explain_intent(text)
            print(f"Input: '{text}'")
            print(f"  → Intent: {result.intent.value.upper()}")
            print(f"  → Confidence: {result.confidence:.3f}")
            print(f"  → Best match: '{result.top_example}'")
            print(f"  → Match score: {result.example_score:.3f}")
            print()
        except Exception as e:
            print(f"❌ Error explaining '{text}': {e}")
            print()


if __name__ == "__main__":
    asyncio.run(test_intent_classifier())
