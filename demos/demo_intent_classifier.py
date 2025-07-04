#!/usr/bin/env python3
"""
Live demo of the EvoAgentX intent classifier.

This script demonstrates the intent classifier with actual OpenAI API calls.
Set OPENAI_API_KEY in your environment before running.

Usage:
    python demo_intent_classifier.py
    python demo_intent_classifier.py --interactive
"""

import asyncio
import argparse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from evoagentx.intents import classify_intent, explain_intent, Intent


def print_header():
    """Print demo header."""
    print("🧠 EvoAgentX Intent Classifier - Live Demo")
    print("=" * 50)
    print()


async def demo_predefined_examples():
    """Demo with predefined examples."""
    print("📋 Testing predefined examples:")
    print("-" * 30)
    
    examples = [
        # Expected ASK classifications
        ("What is machine learning?", Intent.ASK),
        ("Can you explain this concept?", Intent.ASK),
        ("How does neural network training work?", Intent.ASK),
        ("Define artificial intelligence", Intent.ASK),
        ("What are the benefits of automation?", Intent.ASK),
        
        # Expected AGENT classifications  
        ("Create a weekly schedule for my tasks", Intent.AGENT),
        ("Generate a project plan for next month", Intent.AGENT),
        ("Build an outline for my presentation", Intent.AGENT),
        ("Draft a todo list for today", Intent.AGENT),
        ("Organize my meeting notes", Intent.AGENT),
        
        # Ambiguous cases
        ("Help me understand project management", Intent.ASK),
        ("Help me organize my projects", Intent.AGENT),
    ]
    
    correct_predictions = 0
    total_predictions = len(examples)
    
    for text, expected_intent in examples:
        try:
            result = await explain_intent(text)
            is_correct = result.intent == expected_intent
            correct_predictions += is_correct
            
            status = "✅" if is_correct else "❌"
            print(f"{status} '{text}'")
            print(f"   → Predicted: {result.intent.value.upper()} (confidence: {result.confidence:.3f})")
            print(f"   → Expected: {expected_intent.value.upper()}")
            print(f"   → Best match: '{result.top_example}' (score: {result.example_score:.3f})")
            print()
            
        except Exception as e:
            print(f"❌ Error classifying '{text}': {e}")
            print()
    
    accuracy = correct_predictions / total_predictions
    print(f"📊 Accuracy: {correct_predictions}/{total_predictions} ({accuracy:.1%})")
    print()


async def interactive_demo():
    """Interactive demo where user can input custom text."""
    print("🎮 Interactive Mode")
    print("Type messages to classify (press Enter on empty line to exit)")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n💬 Enter message: ").strip()
            
            if not user_input:
                print("👋 Goodbye!")
                break
                
            print("🔄 Classifying...")
            
            # Get detailed explanation
            result = await explain_intent(user_input)
            
            print(f"📋 Results:")
            print(f"   Intent: {result.intent.value.upper()}")
            print(f"   Confidence: {result.confidence:.3f}")
            print(f"   Best match: '{result.top_example}'")
            print(f"   Match score: {result.example_score:.3f}")
            
            # Provide interpretation
            if result.confidence > 0.7:
                confidence_level = "High"
            elif result.confidence > 0.5:
                confidence_level = "Medium"
            else:
                confidence_level = "Low"
                
            print(f"   Interpretation: {confidence_level} confidence {result.intent.value} mode")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="EvoAgentX Intent Classifier Demo")
    parser.add_argument(
        "--interactive", "-i", 
        action="store_true",
        help="Run in interactive mode"
    )
    args = parser.parse_args()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found!")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("Or create a .env file with:")
        print("  OPENAI_API_KEY=your-api-key-here")
        return
    
    print_header()
    
    try:
        if args.interactive:
            await interactive_demo()
        else:
            await demo_predefined_examples()
            
            print("💡 Tip: Run with --interactive to test your own messages!")
            print("Example: python demo_intent_classifier.py --interactive")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\nThis might be due to:")
        print("- Invalid OpenAI API key")
        print("- Network connectivity issues") 
        print("- API quota exceeded")


if __name__ == "__main__":
    asyncio.run(main())
