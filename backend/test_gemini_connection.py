"""
Test Google Gemini API connection.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

print("=" * 60)
print("TESTING GEMINI API CONNECTION")
print("=" * 60)

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file!")
    exit(1)

print(f"\n✅ API Key found: {api_key[:10]}...{api_key[-5:]} (masked)")

# Configure Gemini
try:
    genai.configure(api_key=api_key)
    print("✅ Gemini configured successfully")
except Exception as e:
    print(f"❌ Error configuring Gemini: {e}")
    exit(1)

# Test simple generation
try:
    print("\n📝 Testing text generation...")
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    response = model.generate_content("Say 'Hello! Gemini is working!' in a friendly way.")
    
    print(f"\n✅ Response received:")
    print(f"   {response.text}")
    
    print("\n" + "=" * 60)
    print("🎉 GEMINI CONNECTION TEST SUCCESSFUL!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error generating content: {e}")
    print("\nPossible issues:")
    print("   1. API key is incorrect")
    print("   2. API not enabled (enable at https://aistudio.google.com)")
    print("   3. Network/firewall issue")
    print("\n" + "=" * 60)