#!/usr/bin/env python3
"""
LLM Runner - Simple script to test and run the LLM adapter
"""

import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

def main():
    print("\n" + "="*70)
    print("🤖 LLM ADAPTER - GOOGLE GEMINI")
    print("="*70)
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("\n❌ ERROR: GEMINI_API_KEY not found in .env file")
        print("\nTo fix:")
        print("1. Get key from https://makersuite.google.com/app/apikey")
        print("2. Add to .env: GEMINI_API_KEY=your-key-here")
        return False
    
    print(f"\n✅ API Key found: {api_key[:20]}...")
    
    # Configure
    print("\n📝 Configuring Gemini...")
    try:
        genai.configure(api_key=api_key)
        print("   ✅ Configured")
    except Exception as e:
        print(f"   ❌ Configuration failed: {e}")
        return False
    
    # List models
    print("\n📋 Available models:")
    try:
        models = list(genai.list_models())
        for model in models:
            methods = model.supported_generation_methods
            if "generateContent" in methods:
                print(f"   ✅ {model.name}")
    except Exception as e:
        print(f"   ⚠️  Could not list models: {e}")
    
    # Try common models
    print("\n🔄 Testing models...")
    test_models = [
        "gemini-pro",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-2.0-flash",
    ]
    
    working_model = None
    
    for model_name in test_models:
        try:
            print(f"\n   Testing {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, who are you?")
            
            if response.text:
                print(f"   ✅ {model_name} WORKS!")
                working_model = model_name
                break
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg:
                print(f"   ❌ {model_name} - not available")
            else:
                print(f"   ⚠️  {model_name} - {error_msg[:50]}...")
    
    if not working_model:
        print("\n❌ No working model found")
        return False
    
    # Test with working model
    print(f"\n🎯 Using model: {working_model}")
    print("\n📝 Test generation...")
    
    prompt = "What is an enterprise knowledge base system? Explain in 2-3 sentences."
    print(f"\nPrompt: {prompt}\n")
    
    try:
        model = genai.GenerativeModel(working_model)
        response = model.generate_content(prompt)
        
        print("✅ Response:")
        print("-" * 70)
        print(response.text)
        print("-" * 70)
        
        print("\n✅ LLM IS WORKING!")
        print(f"   Model: {working_model}")
        print(f"   Provider: Google Gemini")
        
        # Update adapter
        print("\n🔧 Updating llm_adapter.py...")
        adapter_file = os.path.join(os.path.dirname(__file__), "agents/llm_adapter.py")
        
        with open(adapter_file, 'r') as f:
            content = f.read()
        
        # Update model name
        content = content.replace('self.model = (\n            "models/gemini-1.5-flash-latest"\n        )', 
                                f'self.model = (\n            "{working_model}"\n        )')
        
        with open(adapter_file, 'w') as f:
            f.write(content)
        
        print(f"   ✅ Updated to use: {working_model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "="*70)
    if success:
        print("✅ LLM IS READY TO USE")
        print("   Run: python main.py")
    else:
        print("❌ LLM NOT WORKING")
        print("   See errors above")
    print("="*70 + "\n")
    
    sys.exit(0 if success else 1)
