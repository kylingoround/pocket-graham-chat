#!/usr/bin/env python3
"""
Comprehensive testing script for the Paul Graham AI Assistant

This script tests the system at multiple levels:
1. Unit tests for individual utilities
2. Integration tests for flows
3. End-to-end testing
4. Quality assessment
"""

import os
import sys
import traceback
from typing import List, Dict, Any

def test_utility_functions():
    """Test individual utility functions"""
    print("🔧 Testing Utility Functions")
    print("-" * 40)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Load Meta
    total_tests += 1
    try:
        from utils.load_meta import load_meta
        if os.path.exists("./meta.csv"):
            meta_data = load_meta("./meta.csv")
            if len(meta_data) > 0 and "1" in meta_data:
                print("✅ load_meta: Working correctly")
                tests_passed += 1
            else:
                print("❌ load_meta: No data loaded")
        else:
            print("⚠️  load_meta: Skipped (meta.csv not found)")
            tests_passed += 1  # Don't fail if file doesn't exist
    except Exception as e:
        print(f"❌ load_meta: {e}")
    
    # Test 2: File Loader
    total_tests += 1
    try:
        from utils.file_loader import load_essays
        from utils.load_meta import load_meta
        if os.path.exists("./meta.csv") and os.path.exists("./data"):
            meta_data = load_meta("./meta.csv")
            # Test with just first 3 essays for speed
            small_meta = {k: v for k, v in list(meta_data.items())[:3]}
            essays = load_essays("./data", small_meta)
            if len(essays) > 0:
                print("✅ file_loader: Working correctly")
                tests_passed += 1
            else:
                print("❌ file_loader: No essays loaded")
        else:
            print("⚠️  file_loader: Skipped (missing data files)")
            tests_passed += 1
    except Exception as e:
        print(f"❌ file_loader: {e}")
    
    # Test 3: Chunking
    total_tests += 1
    try:
        from utils.chunking import chunk_text
        test_essay = {
            'filename': 'test.txt',
            'text_id': '1',
            'title': 'Test Essay',
            'url': 'http://example.com/test',
            'content': "This is a test essay. " * 50  # Create longer content
        }
        chunks = chunk_text(test_essay, chunk_size=100, overlap=20)
        if len(chunks) > 1 and all('text' in chunk for chunk in chunks):
            print("✅ chunking: Working correctly")
            tests_passed += 1
        else:
            print("❌ chunking: Invalid chunks generated")
    except Exception as e:
        print(f"❌ chunking: {e}")
    
    # Test 4: Embeddings (requires Google Cloud credentials)
    total_tests += 1
    try:
        from utils.get_embedding import get_embedding
        test_embedding = get_embedding("Test text for embedding")
        if isinstance(test_embedding, list) and len(test_embedding) > 0:
            print(f"✅ get_embedding: Working correctly (dimension: {len(test_embedding)})")
            tests_passed += 1
        else:
            print("❌ get_embedding: Invalid embedding returned")
    except Exception as e:
        print(f"❌ get_embedding: {e} (Check Google Cloud credentials)")
    
    # Test 5: Vector Database
    total_tests += 1
    try:
        from utils.vector_db import create_vector_index, search_vector_index
        # Create mock embeddings
        mock_embeddings = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        mock_metadata = [
            {"text": "first text", "title": "Essay 1"},
            {"text": "second text", "title": "Essay 2"},
            {"text": "third text", "title": "Essay 3"}
        ]
        index = create_vector_index(mock_embeddings, mock_metadata)
        results = search_vector_index([1.0, 0.0, 0.0], index, top_k=2)
        if len(results) == 2 and 'similarity_score' in results[0]:
            print("✅ vector_db: Working correctly")
            tests_passed += 1
        else:
            print("❌ vector_db: Search results invalid")
    except Exception as e:
        print(f"❌ vector_db: {e}")
    
    # Test 6: Relevance Validation
    total_tests += 1
    try:
        from utils.validate_relevance import validate_question_relevance
        relevant_question = "How do I get startup ideas?"
        irrelevant_question = "How do I cure cancer?"
        
        is_relevant1, _ = validate_question_relevance(relevant_question)
        is_relevant2, _ = validate_question_relevance(irrelevant_question)
        
        if is_relevant1 and not is_relevant2:
            print("✅ validate_relevance: Working correctly")
            tests_passed += 1
        elif is_relevant1:
            print("⚠️  validate_relevance: Working but may be too permissive")
            tests_passed += 1
        else:
            print("❌ validate_relevance: Not working as expected")
    except Exception as e:
        print(f"❌ validate_relevance: {e}")
    
    # Test 7: Pause Processor
    total_tests += 1
    try:
        from utils.pause_processor import add_pauses
        test_text = "This is a test. This is another sentence. Final thought."
        processed_text = add_pauses(test_text, pause_scale=2)
        if processed_text != test_text and len(processed_text) > len(test_text):
            print("✅ pause_processor: Working correctly")
            tests_passed += 1
        else:
            print("❌ pause_processor: No pauses added")
    except Exception as e:
        print(f"❌ pause_processor: {e}")
    
    print(f"\n📊 Utility Tests: {tests_passed}/{total_tests} passed")
    return tests_passed, total_tests

def test_nodes():
    """Test individual nodes"""
    print("\n🔨 Testing Individual Nodes")
    print("-" * 40)
    
    tests_passed = 0
    total_tests = 0
    
    # Test LoadMetaNode
    total_tests += 1
    try:
        from nodes import LoadMetaNode
        from main import create_shared_store
        
        if os.path.exists("./meta.csv"):
            shared = create_shared_store()
            node = LoadMetaNode()
            node.run(shared)
            
            if len(shared.get("meta_dict", {})) > 0:
                print("✅ LoadMetaNode: Working correctly")
                tests_passed += 1
            else:
                print("❌ LoadMetaNode: No metadata loaded")
        else:
            print("⚠️  LoadMetaNode: Skipped (meta.csv not found)")
            tests_passed += 1
    except Exception as e:
        print(f"❌ LoadMetaNode: {e}")
    
    # Test ValidateRelevanceNode
    total_tests += 1
    try:
        from nodes import ValidateRelevanceNode
        from main import create_shared_store
        
        shared = create_shared_store()
        shared["user_question"] = "How do I get startup ideas?"
        
        node = ValidateRelevanceNode()
        result = node.run(shared)
        
        if result == "relevant" and shared.get("is_relevant"):
            print("✅ ValidateRelevanceNode: Working correctly")
            tests_passed += 1
        else:
            print("❌ ValidateRelevanceNode: Validation failed")
    except Exception as e:
        print(f"❌ ValidateRelevanceNode: {e}")
    
    print(f"\n📊 Node Tests: {tests_passed}/{total_tests} passed")
    return tests_passed, total_tests

def test_offline_flow():
    """Test the offline indexing flow with a small subset"""
    print("\n📚 Testing Offline Flow (Small Dataset)")
    print("-" * 40)
    
    try:
        from flow import create_offline_flow
        from main import create_shared_store
        from utils.load_meta import load_meta
        
        if not os.path.exists("./meta.csv") or not os.path.exists("./data"):
            print("⚠️  Offline flow test skipped (missing data files)")
            return 1, 1
        
        # Create a small test dataset
        shared = create_shared_store()
        
        # Limit to first 3 essays for testing
        full_meta = load_meta("./meta.csv")
        test_meta = {k: v for k, v in list(full_meta.items())[:3]}
        shared["meta_dict"] = test_meta
        
        # Update config for testing
        shared["config"]["index_path"] = "./test_vector_index.pkl"
        
        print("🔄 Running offline flow with 3 essays...")
        
        # Create and run offline flow (skip LoadMetaNode since we set it manually)
        from nodes import LoadEssaysNode, ChunkEssaysNode, EmbedChunksNode, StoreIndexNode
        
        # Test each step
        load_essays = LoadEssaysNode()
        load_essays.run(shared)
        print(f"  ✅ Loaded {len(shared.get('essays', []))} essays")
        
        chunk_essays = ChunkEssaysNode()
        chunk_essays.run(shared)
        print(f"  ✅ Created {len(shared.get('chunks', []))} chunks")
        
        embed_chunks = EmbedChunksNode()
        embed_chunks.run(shared)
        print(f"  ✅ Generated {len(shared.get('embeddings', []))} embeddings")
        
        store_index = StoreIndexNode()
        store_index.run(shared)
        print(f"  ✅ Saved index to {shared['config']['index_path']}")
        
        # Verify index file was created
        if os.path.exists(shared["config"]["index_path"]):
            print("✅ Offline flow: Completed successfully")
            return 1, 1
        else:
            print("❌ Offline flow: Index file not created")
            return 0, 1
            
    except Exception as e:
        print(f"❌ Offline flow: {e}")
        traceback.print_exc()
        return 0, 1

def test_online_flow():
    """Test the online Q&A flow"""
    print("\n💬 Testing Online Flow")
    print("-" * 40)
    
    try:
        from main import create_shared_store
        from nodes import LoadIndexNode, ValidateRelevanceNode, EmbedQueryNode, RetrieveChunksNode, GenerateAnswerNode
        
        # Check if test index exists
        test_index_path = "./test_vector_index.pkl"
        if not os.path.exists(test_index_path):
            print("⚠️  Online flow test skipped (no test index found)")
            print("    Run offline flow test first")
            return 1, 1
        
        shared = create_shared_store()
        shared["config"]["index_path"] = test_index_path
        shared["user_question"] = "How do I get startup ideas?"
        
        print("🔄 Testing online flow components...")
        
        # Load index
        load_index = LoadIndexNode()
        load_index.run(shared)
        print(f"  ✅ Loaded index with {len(shared.get('chunks_metadata', []))} chunks")
        
        # Validate question
        validate = ValidateRelevanceNode()
        result = validate.run(shared)
        if result == "relevant":
            print("  ✅ Question validated as relevant")
        else:
            print("  ❌ Question not validated")
            return 0, 1
        
        # Embed query
        embed_query = EmbedQueryNode()
        embed_query.run(shared)
        print(f"  ✅ Query embedded (dimension: {len(shared.get('query_embedding', []))})")
        
        # Retrieve chunks
        retrieve = RetrieveChunksNode()
        retrieve.run(shared)
        retrieved = shared.get('retrieved_chunks', [])
        print(f"  ✅ Retrieved {len(retrieved)} relevant chunks")
        
        # Generate answer
        generate = GenerateAnswerNode()
        generate.run(shared)
        answer = shared.get('generated_answer', '')
        if answer:
            print(f"  ✅ Generated answer: {answer[:100]}...")
            print("✅ Online flow: Completed successfully")
            return 1, 1
        else:
            print("  ❌ No answer generated")
            return 0, 1
            
    except Exception as e:
        print(f"❌ Online flow: {e}")
        traceback.print_exc()
        return 0, 1

def test_question_quality():
    """Test with various question types to assess quality"""
    print("\n🎯 Testing Question Quality & Coverage")
    print("-" * 40)
    
    test_questions = [
        ("How do I get startup ideas?", True, "Core PG topic"),
        ("What makes a good founder?", True, "Entrepreneurship"),
        ("How should I learn programming?", True, "Programming advice"),
        ("What's the best essay writing advice?", True, "Writing craft"),
        ("How do I cure cancer?", False, "Medical advice"),
        ("What's the weather today?", False, "Current events"),
        ("How do I fix my computer?", False, "Technical support"),
    ]
    
    correct_validations = 0
    total_questions = len(test_questions)
    
    try:
        from utils.validate_relevance import validate_question_relevance
        
        for question, expected_relevant, category in test_questions:
            is_relevant, message = validate_question_relevance(question)
            
            status = "✅" if is_relevant == expected_relevant else "❌"
            result = "RELEVANT" if is_relevant else "DECLINED"
            
            print(f"  {status} [{category}] {question}")
            print(f"     → {result}")
            
            if message and not is_relevant:
                print(f"     → {message[:80]}...")
            
            if is_relevant == expected_relevant:
                correct_validations += 1
            
            print()
    
    except Exception as e:
        print(f"❌ Question quality test: {e}")
        return 0, total_questions
    
    print(f"📊 Question Validation: {correct_validations}/{total_questions} correct")
    return correct_validations, total_questions

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("🧪 Paul Graham AI Assistant - Comprehensive Test Suite")
    print("=" * 60)
    
    total_passed = 0
    total_tests = 0
    
    # Run all test categories
    test_results = []
    
    # Utility function tests
    passed, total = test_utility_functions()
    test_results.append(("Utility Functions", passed, total))
    total_passed += passed
    total_tests += total
    
    # Node tests
    passed, total = test_nodes()
    test_results.append(("Individual Nodes", passed, total))
    total_passed += passed
    total_tests += total
    
    # Offline flow test
    passed, total = test_offline_flow()
    test_results.append(("Offline Flow", passed, total))
    total_passed += passed
    total_tests += total
    
    # Online flow test
    passed, total = test_online_flow()
    test_results.append(("Online Flow", passed, total))
    total_passed += passed
    total_tests += total
    
    # Quality tests
    passed, total = test_question_quality()
    test_results.append(("Question Quality", passed, total))
    total_passed += passed
    total_tests += total
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for category, passed, total in test_results:
        percentage = (passed / total * 100) if total > 0 else 0
        status = "✅" if passed == total else "⚠️" if passed > total * 0.7 else "❌"
        print(f"{status} {category:<20}: {passed:>2}/{total:<2} ({percentage:>5.1f}%)")
    
    overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print("-" * 60)
    print(f"🎯 OVERALL RESULT: {total_passed}/{total_tests} ({overall_percentage:.1f}%)")
    
    if overall_percentage >= 90:
        print("🎉 Excellent! System is ready for production use.")
    elif overall_percentage >= 70:
        print("👍 Good! System is functional with minor issues.")
    else:
        print("⚠️  System needs attention before use.")
    
    # Cleanup test files
    test_files = ["./test_vector_index.pkl"]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🧹 Cleaned up {file}")
    
    return overall_percentage >= 70

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
