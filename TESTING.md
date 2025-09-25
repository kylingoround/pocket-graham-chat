# Testing Guide for Paul Graham AI Assistant

This guide provides multiple testing approaches to validate the system at different levels.

## Quick Testing Strategy

### 1. 🚀 Smoke Test (2 minutes)

Quick check to ensure basic functionality works:

```bash
python quick_test.py
```

This tests:

- ✅ File prerequisites (meta.csv, data/ directory)
- ✅ Module imports
- ✅ Basic utility functions
- ✅ API connectivity (LLM + embeddings)

### 2. 🧪 Comprehensive Test (10-15 minutes)

Full system validation with actual data processing:

```bash
python test_system.py
```

This tests:

- ✅ All utility functions with real data
- ✅ Individual node functionality
- ✅ Complete offline flow (small dataset)
- ✅ Complete online flow
- ✅ Question quality and validation

### 3. 🎯 Manual End-to-End Test (5 minutes)

Real-world usage simulation:

```bash
# Step 1: Build the index
python main.py --mode offline

# Step 2: Test single Q&A
python main.py --mode online

# Step 3: Test continuous chat
python main.py --mode continuous
```

## Detailed Testing Approaches

### Prerequisites Setup

Before testing, ensure you have:

1. **Data Files**:

   ```bash
   ls meta.csv          # Essay metadata
   ls data/ | head      # 354 essay files (1.txt, 2.txt, etc.)
   ```

2. **Google Cloud Credentials**:

   ```bash
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
   ```

3. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Testing Individual Components

#### Test Utility Functions

```python
# Test metadata loading
from utils.load_meta import load_meta
meta = load_meta("meta.csv")
print(f"Loaded {len(meta)} essays")

# Test embeddings
from utils.get_embedding import get_embedding
embedding = get_embedding("Test text")
print(f"Embedding dimension: {len(embedding)}")

# Test LLM
from utils.call_llm import call_llm
response = call_llm("What is a startup?")
print(f"LLM response: {response}")
```

#### Test Individual Nodes

```python
from nodes import LoadMetaNode, ValidateRelevanceNode
from main import create_shared_store

# Test metadata loading
shared = create_shared_store()
meta_node = LoadMetaNode()
meta_node.run(shared)
print(f"Meta dict size: {len(shared['meta_dict'])}")

# Test question validation
shared["user_question"] = "How do I get startup ideas?"
validate_node = ValidateRelevanceNode()
result = validate_node.run(shared)
print(f"Validation result: {result}")
```

### Performance Testing

#### Measure Processing Times

```bash
# Time the offline indexing
time python main.py --mode offline

# Time query processing
time python -c "
from main import create_shared_store
from nodes import LoadIndexNode, EmbedQueryNode, RetrieveChunksNode
import time

shared = create_shared_store()
shared['user_question'] = 'How do I get startup ideas?'

start = time.time()
LoadIndexNode().run(shared)
print(f'Index loading: {time.time() - start:.2f}s')

start = time.time()
EmbedQueryNode().run(shared)
print(f'Query embedding: {time.time() - start:.2f}s')

start = time.time()
RetrieveChunksNode().run(shared)
print(f'Chunk retrieval: {time.time() - start:.2f}s')
"
```

#### Memory Usage

```bash
# Monitor memory during indexing
python -c "
import psutil
import os
from main import run_offline_indexing

process = psutil.Process(os.getpid())
print(f'Memory before: {process.memory_info().rss / 1024 / 1024:.1f} MB')

run_offline_indexing()

print(f'Memory after: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

### Quality Testing

#### Test Question Categories

```python
test_questions = [
    # Should be relevant
    "How do I get startup ideas?",
    "What makes a good founder?",
    "How should I learn programming?",
    "What's the best way to write essays?",
    "How do I scale a startup?",

    # Should be declined
    "How do I cure cancer?",
    "What's the weather today?",
    "How do I fix my computer?",
    "What's Paul Graham's home address?",
    "How do I invest in stocks?"
]

from utils.validate_relevance import validate_question_relevance

for question in test_questions:
    is_relevant, message = validate_question_relevance(question)
    print(f"{'✅' if is_relevant else '❌'} {question}")
    if message:
        print(f"   → {message}")
```

#### Test Response Quality

```python
# Test with the full system
from main import create_shared_store
from flow import create_online_flow

shared = create_shared_store()
flow = create_online_flow()

test_questions = [
    "How do I get startup ideas?",
    "What makes programming fun?",
    "How should I approach learning?",
]

for question in test_questions:
    print(f"\nQuestion: {question}")
    shared["user_question"] = question
    flow.run(shared)

    response = shared.get("formatted_response", {})
    print(f"Answer: {response.get('text', 'No response')}")
    print(f"Citations: {len(response.get('citations', []))}")
```

### Error Handling Testing

#### Test Missing Files

```bash
# Test with missing data
mv data data_backup
python main.py --mode offline  # Should fail gracefully

mv meta.csv meta_backup
python main.py --mode offline  # Should fail gracefully

# Restore files
mv data_backup data
mv meta_backup meta.csv
```

#### Test API Failures

```python
# Test with invalid credentials
import os
old_project = os.environ.get('GOOGLE_CLOUD_PROJECT')
os.environ['GOOGLE_CLOUD_PROJECT'] = 'invalid-project'

from utils.call_llm import call_llm
try:
    call_llm("test")
except Exception as e:
    print(f"Expected error: {e}")

# Restore
if old_project:
    os.environ['GOOGLE_CLOUD_PROJECT'] = old_project
```

### Load Testing

#### Test Multiple Concurrent Questions

```python
import threading
import time
from main import create_shared_store
from nodes import LoadIndexNode, ValidateRelevanceNode, EmbedQueryNode, RetrieveChunksNode

# Load index once
shared = create_shared_store()
LoadIndexNode().run(shared)

def process_question(question, thread_id):
    local_shared = shared.copy()
    local_shared["user_question"] = question

    start = time.time()
    ValidateRelevanceNode().run(local_shared)
    EmbedQueryNode().run(local_shared)
    RetrieveChunksNode().run(local_shared)
    end = time.time()

    print(f"Thread {thread_id}: {end - start:.2f}s")

# Test 5 concurrent questions
threads = []
questions = ["How do I get startup ideas?"] * 5

for i, question in enumerate(questions):
    thread = threading.Thread(target=process_question, args=(question, i))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
```

## Expected Results

### Smoke Test Results

- **Prerequisites**: All files present, credentials set
- **Imports**: All modules load successfully
- **Basic Functions**: Chunking, pauses, vector DB work
- **API Connectivity**: LLM and embedding APIs respond

### Comprehensive Test Results

- **Utility Functions**: 6-7/7 pass (embedding may fail without credentials)
- **Individual Nodes**: 2/2 pass
- **Offline Flow**: Creates index with ~1000-2000 chunks
- **Online Flow**: Retrieves relevant chunks and generates answers
- **Question Quality**: 7/7 validation decisions correct

### Performance Expectations

- **Offline Indexing**: 5-15 minutes for 354 essays
- **Query Processing**: 2-5 seconds per question
- **Memory Usage**: ~500MB-1GB during indexing
- **Index Size**: ~50-100MB saved to disk

## Troubleshooting

### Common Issues

1. **"Vector index not found"**

   ```bash
   python main.py --mode offline  # Run indexing first
   ```

2. **Google Cloud authentication errors**

   ```bash
   export GOOGLE_CLOUD_PROJECT="your-project"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"
   ```

3. **Missing dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Out of memory during indexing**

   ```python
   # Reduce batch size in nodes.py
   # Or process fewer essays for testing
   ```

5. **Slow response times**
   ```python
   # Disable audio generation in continuous mode
   # Reduce max_chunks in config
   ```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run your test with verbose output
```

## Automated Testing Pipeline

For CI/CD, create a test pipeline:

```bash
#!/bin/bash
# test_pipeline.sh

echo "🧪 Running Paul Graham AI Test Pipeline"

# 1. Quick smoke test
echo "Step 1: Smoke test"
python quick_test.py || exit 1

# 2. Comprehensive test with small dataset
echo "Step 2: Comprehensive test"
python test_system.py || exit 1

# 3. Performance benchmark
echo "Step 3: Performance test"
time python main.py --mode offline
time python -c "
from main import create_shared_store
from flow import create_online_flow
shared = create_shared_store()
shared['user_question'] = 'How do I get startup ideas?'
create_online_flow().run(shared)
"

echo "✅ All tests passed!"
```

This comprehensive testing approach ensures your Paul Graham AI Assistant is robust, performant, and ready for production use!
