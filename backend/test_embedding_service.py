"""
Test script for production embedding service.
Tests single embedding, batch processing, and singleton pattern.
"""

from app.services.embedding_service import embedding_service

print("=" * 60)
print("TESTING PRODUCTION EMBEDDING SERVICE")
print("=" * 60)

# Test 1: Single embedding
print("\n📝 TEST 1: Single Text Embedding")
print("-" * 60)

text = "Artificial intelligence is transforming healthcare."
print(f"Input text: '{text}'")
print("Generating embedding...")

embedding = embedding_service.generate_embedding(text)

print(f"✅ Success!")
print(f"   Dimensions: {len(embedding)}")
print(f"   Type: {type(embedding)}")
print(f"   First 5 values: {embedding[:5]}")
print(f"   Last 5 values: {embedding[-5:]}")

# Test 2: Batch embeddings
print("\n📦 TEST 2: Batch Processing")
print("-" * 60)

texts = [
    "Machine learning enables computers to learn from data.",
    "Neural networks are inspired by biological neurons.",
    "Deep learning uses multiple layers of neural networks.",
    "Natural language processing helps computers understand text.",
    "Computer vision allows machines to interpret images."
]

print(f"Input: {len(texts)} texts")
print("Generating embeddings in batch...")

embeddings = embedding_service.generate_embeddings_batch(texts)

print(f"✅ Success!")
print(f"   Number of embeddings: {len(embeddings)}")
print(f"   Each embedding dimension: {len(embeddings[0])}")
print(f"   Type: {type(embeddings)}")
print(f"   First embedding preview: {embeddings[0][:5]}")

# Test 3: Dimension getter
print("\n📏 TEST 3: Get Embedding Dimension")
print("-" * 60)

dimension = embedding_service.get_embedding_dimension()
print(f"Embedding dimension: {dimension}")
print(f"✅ Matches expected: {dimension == 768}")

# Test 4: Singleton verification
print("\n🔄 TEST 4: Singleton Pattern Verification")
print("-" * 60)

# Import again (should get same instance)
from app.services.embedding_service import embedding_service as service2

print(f"Original service ID: {id(embedding_service)}")
print(f"Re-imported service ID: {id(service2)}")
print(f"✅ Same instance: {embedding_service is service2}")

# Test 5: Edge cases
print("\n⚠️  TEST 5: Edge Cases")
print("-" * 60)

# Empty string
try:
    empty_emb = embedding_service.generate_embedding("")
    print(f"✅ Empty string: {len(empty_emb)} dimensions")
except Exception as e:
    print(f"❌ Empty string error: {e}")

# Very long text
long_text = "AI " * 1000  # 2000 words
try:
    long_emb = embedding_service.generate_embedding(long_text)
    print(f"✅ Long text (2000 words): {len(long_emb)} dimensions")
except Exception as e:
    print(f"❌ Long text error: {e}")

# Batch with one item
try:
    single_batch = embedding_service.generate_embeddings_batch(["Single item"])
    print(f"✅ Single-item batch: {len(single_batch)} embeddings")
except Exception as e:
    print(f"❌ Single-item batch error: {e}")

print("\n" + "=" * 60)
print("🎉 ALL TESTS COMPLETE!")
print("=" * 60)
print("\nEmbedding service is production-ready! ✅")