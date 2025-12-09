"""
Test chunking service functionality.
"""

from app.services.chunking_service import chunk_text

print("=" * 60)
print("TESTING CHUNKING SERVICE")
print("=" * 60)

# Test 1: Normal text
print("\n📝 TEST 1: Normal Document")
print("-" * 60)

text = """
Artificial intelligence is transforming healthcare through advanced diagnostic systems. 
Machine learning algorithms can now detect diseases from medical images with accuracy 
matching or exceeding human experts. Natural language processing enables automated 
analysis of clinical notes and medical literature. These technologies are being deployed 
in hospitals worldwide, improving patient outcomes while reducing healthcare costs.

Deep learning models have shown remarkable success in radiology, pathology, and genomics. 
Convolutional neural networks can identify tumors, fractures, and other abnormalities 
in X-rays, CT scans, and MRIs. Recurrent neural networks process time-series data from 
patient monitoring systems to predict adverse events before they occur.

The integration of AI into medical practice represents a fundamental shift in healthcare 
delivery. However, challenges remain around data privacy, algorithmic bias, and regulatory 
approval. Ongoing research focuses on making AI systems more transparent, reliable, and 
equitable for all patient populations.
"""

chunks = chunk_text(text.strip(), chunk_size=200, overlap=30)

print(f"Original text: {len(text)} characters")
print(f"Chunks created: {len(chunks)}")
print(f"\nFirst chunk:\n{chunks[0][:100]}...")
print(f"\nLast chunk:\n{chunks[-1][:100]}...")

# Test 2: Short text
print("\n📝 TEST 2: Short Text (No Chunking Needed)")
print("-" * 60)

short_text = "AI is transforming healthcare."
chunks = chunk_text(short_text, chunk_size=500, overlap=50)

print(f"Text: '{short_text}'")
print(f"Chunks: {len(chunks)}")
print(f"Result: {chunks}")

# Test 3: Empty text
print("\n📝 TEST 3: Empty Text")
print("-" * 60)

empty_text = ""
chunks = chunk_text(empty_text)

print(f"Text: '{empty_text}'")
print(f"Chunks: {len(chunks)}")
print(f"Result: {chunks}")

# Test 4: Check overlap
print("\n📝 TEST 4: Verify Overlap")
print("-" * 60)

text = "A" * 100 + "B" * 100 + "C" * 100
chunks = chunk_text(text, chunk_size=100, overlap=20)

print(f"Text length: {len(text)}")
print(f"Chunks: {len(chunks)}")
print(f"Chunk 1 ends with: '{chunks[0][-20:]}'")
print(f"Chunk 2 starts with: '{chunks[1][:20]}'")
print(f"Overlap preserved: {chunks[0][-20:] == chunks[1][:20]}")

print("\n" + "=" * 60)
print("🎉 CHUNKING SERVICE TESTS COMPLETE!")
print("=" * 60)