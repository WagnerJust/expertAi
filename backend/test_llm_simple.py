#!/usr/bin/env python3
"""
Simple test to verify LLM service connectivity
"""
import asyncio
import sys
import os
sys.path.append('/Users/justin/LLMS/App/backend')

from app.rag_components.llm_handler import health_check_llm_service, generate_answer_from_context

async def test_llm_service():
    """Test LLM service connectivity"""
    print("🧪 Testing LLM Service Connection")
    print("=" * 40)
    
    # 1. Health check
    print("\n1. Testing LLM service health...")
    is_healthy = await health_check_llm_service()
    print(f"   LLM Service Health: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
    
    if is_healthy:
        # 2. Simple generation test
        print("\n2. Testing simple text generation...")
        test_prompt = "What is artificial intelligence?"
        response = await generate_answer_from_context(
            test_prompt,
            max_tokens=100,
            temperature=0.7
        )
        
        if response:
            print(f"   ✅ Generated response ({len(response)} chars):")
            print(f"   Response: {response[:200]}{'...' if len(response) > 200 else ''}")
        else:
            print("   ❌ No response generated")
    
    print("\n" + "=" * 40)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_llm_service())
