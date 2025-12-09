"""
Setup Pinecone index for RAG system.
Deletes existing index if present and creates new one with correct dimensions.
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import time

# Load environment variables
load_dotenv()

# Configuration
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rag-documents")
EMBEDDING_DIMENSION = 768  # all-mpnet-base-v2 dimension
METRIC = "cosine"

print("=" * 60)
print("PINECONE INDEX SETUP")
print("=" * 60)

# Initialize Pinecone
api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=api_key)

print(f"\n📋 Target index name: {INDEX_NAME}")
print(f"📐 Required dimension: {EMBEDDING_DIMENSION}")
print(f"📏 Similarity metric: {METRIC}")

# Check if index already exists
existing_indexes = pc.list_indexes()
index_names = [idx['name'] for idx in existing_indexes]

if INDEX_NAME in index_names:
    print(f"\n⚠️  Index '{INDEX_NAME}' already exists!")
    
    # Get existing index details
    existing_index = [idx for idx in existing_indexes if idx['name'] == INDEX_NAME][0]
    existing_dimension = existing_index['dimension']
    
    print(f"   Existing dimension: {existing_dimension}")
    print(f"   Required dimension: {EMBEDDING_DIMENSION}")
    
    if existing_dimension != EMBEDDING_DIMENSION:
        print(f"\n❌ DIMENSION MISMATCH!")
        print(f"   Existing: {existing_dimension}")
        print(f"   Required: {EMBEDDING_DIMENSION}")
        print(f"\n🗑️  Deleting existing index...")
        
        pc.delete_index(INDEX_NAME)
        print(f"✅ Index '{INDEX_NAME}' deleted")
        
        # Wait for deletion to complete
        print("⏳ Waiting for deletion to complete...")
        time.sleep(5)
    else:
        print(f"\n✅ Dimensions match! Index is already correctly configured.")
        print("\n" + "=" * 60)
        print("🎉 INDEX READY TO USE!")
        print("=" * 60)
        exit(0)

# Create new index
print(f"\n🔨 Creating new index '{INDEX_NAME}'...")

try:
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIMENSION,
        metric=METRIC,
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )
    
    print(f"✅ Index '{INDEX_NAME}' created successfully!")
    
    # Wait for index to be ready
    print("⏳ Waiting for index to be ready...")
    time.sleep(10)
    
    # Verify index
    indexes = pc.list_indexes()
    new_index = [idx for idx in indexes if idx['name'] == INDEX_NAME][0]
    
    print("\n📊 Index details:")
    print(f"   Name: {new_index['name']}")
    print(f"   Dimension: {new_index['dimension']}")
    print(f"   Metric: {new_index['metric']}")
    print(f"   Status: Ready")
    
    print("\n" + "=" * 60)
    print("🎉 INDEX SETUP COMPLETE!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR creating index:")
    print(f"   {str(e)}")
    print("\n" + "=" * 60)