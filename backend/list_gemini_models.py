"""
List available Gemini models.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("=" * 60)
print("LISTING AVAILABLE GEMINI MODELS")
print("=" * 60)

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("\n📋 Available models:\n")

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description}")
            print(f"   Supported: {model.supported_generation_methods}")
            print()
    
    print("=" * 60)
    print("Use one of the names above in your code!")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Error listing models: {e}")