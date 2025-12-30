"""
Test Pinecone connection and API key.
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

print("=" * 60)
print("TESTING PINECONE CONNECTION")
print("=" * 60)

# Get API key from environment
api_key = os.getenv("PINECONE_API_KEY")

if not api_key:
    print("❌ ERROR: PINECONE_API_KEY not found in .env file!")
    exit(1)

print(f"\n✅ API Key found: {api_key[:10]}...{api_key[-5:]} (masked)")

# Initialize Pinecone client
try:
    print("\n📡 Connecting to Pinecone...")
    pc = Pinecone(api_key=api_key)
    print("✅ Connection successful!")
    
    # List existing indexes
    print("\n📋 Listing existing indexes...")
    indexes = pc.list_indexes()
    
    if indexes:
        print(f"✅ Found {len(indexes)} existing indexes:")
        for index in indexes:
            print(f"   - {index['name']} (dimension: {index['dimension']}, metric: {index['metric']})")
    else:
        print("✅ No existing indexes (this is normal for new accounts)")
    
    print("\n" + "=" * 60)
    print("🎉 PINECONE CONNECTION TEST SUCCESSFUL!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR connecting to Pinecone:")
    print(f"   {str(e)}")
    print("\nPossible issues:")
    print("   1. API key is incorrect")
    print("   2. Internet connection problem")
    print("   3. Pinecone service issue")
    print("\n" + "=" * 60)