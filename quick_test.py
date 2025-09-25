#!/usr/bin/env python3
"""
Quick smoke test for the Paul Graham AI Assistant
Run this before doing a full system test to catch basic issues
"""

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

def load_environment():
    """Load environment variables from a .env file if available."""
    env_override = os.getenv("POCKET_GRAHAM_ENV_FILE")
    default_env = Path(__file__).resolve().parent / ".env"
    env_path = Path(env_override).expanduser() if env_override else default_env

    if load_dotenv is None:
        print("🌱 Environment: python-dotenv not installed; skipping .env loading")
        return False

    if load_dotenv(env_path):
        print(f"🌱 Environment: Loaded variables from {env_path}")
        return True

    print(f"🌱 Environment: No .env file found at {env_path} (skipping)")
    return False

def check_prerequisites():
    """Check if all required files and dependencies are available"""
    print("🔍 Checking Prerequisites...")
    
    required_files = [
        ("meta.csv", "Essay metadata file"),
        ("data/", "Essay data directory"),
        ("data/1.txt", "Sample essay file"),
    ]
    
    missing_files = []
    for file_path, description in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {description}: {file_path}")
        else:
            print(f"  ❌ {description}: {file_path} (MISSING)")
            missing_files.append(file_path)
    
    # Check environment variables
    env_vars = [
        ("GOOGLE_CLOUD_PROJECT", "Google Cloud Project ID"),
        ("GOOGLE_APPLICATION_CREDENTIALS", "Google Cloud Credentials"),
    ]
    
    missing_env = []
    for var, description in env_vars:
        if os.getenv(var):
            print(f"  ✅ {description}: Set")
        else:
            print(f"  ⚠️  {description}: Not set (required for LLM/embeddings)")
            missing_env.append(var)
    
    return len(missing_files) == 0, missing_files, missing_env

def test_imports():
    """Test that all modules can be imported"""
    print("\n📦 Testing Imports...")
    
    modules_to_test = [
        ("pocketflow", "PocketFlow framework"),
        ("utils.call_llm", "LLM utility"),
        ("utils.get_embedding", "Embedding utility"),
        ("utils.load_meta", "Metadata loader"),
        ("nodes", "Node definitions"),
        ("flow", "Flow definitions"),
        ("main", "Main application"),
    ]
    
    import_failures = []
    for module, description in modules_to_test:
        try:
            __import__(module)
            print(f"  ✅ {description}: {module}")
        except Exception as e:
            print(f"  ❌ {description}: {module} ({e})")
            import_failures.append(module)
    
    return len(import_failures) == 0, import_failures

def test_basic_functionality():
    """Test basic functionality without heavy operations"""
    print("\n⚡ Testing Basic Functionality...")
    
    try:
        # Test metadata loading
        from utils.load_meta import load_meta
        if os.path.exists("meta.csv"):
            meta_data = load_meta("meta.csv")
            print(f"  ✅ Metadata loading: {len(meta_data)} essays found")
        else:
            print("  ⚠️  Metadata loading: Skipped (no meta.csv)")
        
        # Test chunking
        from utils.chunking import chunk_text
        test_essay = {
            'filename': 'test.txt',
            'text_id': '1', 
            'title': 'Test Essay',
            'url': 'http://test.com',
            'content': "This is a test sentence. " * 20
        }
        chunks = chunk_text(test_essay, chunk_size=100, overlap=20)
        print(f"  ✅ Text chunking: {len(chunks)} chunks created")
        
        # Test pause processing
        from utils.pause_processor import add_pauses
        test_text = "This is a test. Another sentence here."
        processed = add_pauses(test_text, pause_scale=2)
        print(f"  ✅ Pause processing: Text enhanced")
        
        # Test vector database (without embeddings)
        from utils.vector_db import create_vector_index
        mock_embeddings = [[1.0, 0.0], [0.0, 1.0]]
        mock_metadata = [{"text": "test1"}, {"text": "test2"}]
        index = create_vector_index(mock_embeddings, mock_metadata)
        print(f"  ✅ Vector database: Index created")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Basic functionality test failed: {e}")
        return False

def test_api_connectivity():
    """Test connectivity to external APIs"""
    print("\n🌐 Testing API Connectivity...")
    
    # Test LLM API
    try:
        from utils.call_llm import call_llm
        response = call_llm("Say 'test successful' if you can read this.")
        if response and len(response) > 0:
            # Handle Unicode characters safely
            safe_response = response[:50].encode('ascii', 'ignore').decode('ascii')
            print(f"  ✅ LLM API: Connected (response: {safe_response}...)")
            llm_working = True
        else:
            print("  ❌ LLM API: No response received")
            llm_working = False
    except Exception as e:
        print(f"  ❌ LLM API: {e}")
        llm_working = False
    
    # Test Embedding API
    try:
        from utils.get_embedding import get_embedding
        embedding = get_embedding("test text")
        if embedding and len(embedding) > 0:
            print(f"  ✅ Embedding API: Connected (dimension: {len(embedding)})")
            embedding_working = True
        else:
            print("  ❌ Embedding API: No embedding received")
            embedding_working = False
    except Exception as e:
        print(f"  ❌ Embedding API: {e}")
        embedding_working = False
    
    return llm_working and embedding_working

def run_quick_test():
    """Run all quick tests"""
    print("🚀 Paul Graham AI Assistant - Quick Smoke Test")
    print("=" * 50)
    
    # Load environment variables from .env file
    load_environment()
    
    # Check prerequisites
    files_ok, missing_files, missing_env = check_prerequisites()
    
    # Test imports
    imports_ok, failed_imports = test_imports()
    
    # Test basic functionality
    basic_ok = test_basic_functionality()
    
    # Test API connectivity
    api_ok = test_api_connectivity()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 QUICK TEST SUMMARY")
    print("=" * 50)
    
    checks = [
        ("Prerequisites", files_ok),
        ("Module Imports", imports_ok),
        ("Basic Functions", basic_ok),
        ("API Connectivity", api_ok),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    print("-" * 50)
    
    if all_passed:
        print("🎉 All quick tests passed! System looks ready.")
        print("💡 Next steps:")
        print("   1. Run full test: python test_system.py")
        print("   2. Try offline mode: python main.py --mode offline")
        print("   3. Start chatting: python main.py --mode continuous")
    else:
        print("⚠️  Some issues found. Please fix before proceeding:")
        
        if missing_files:
            print(f"   📁 Missing files: {', '.join(missing_files)}")
        
        if missing_env:
            print(f"   🔧 Missing env vars: {', '.join(missing_env)}")
            print("      Set up Google Cloud credentials:")
            print("      export GOOGLE_CLOUD_PROJECT='your-project-id'")
            print("      export GOOGLE_APPLICATION_CREDENTIALS='path/to/credentials.json'")
        
        if failed_imports:
            print(f"   📦 Failed imports: {', '.join(failed_imports)}")
            print("      Try: pip install -r requirements.txt")
    
    return all_passed

if __name__ == "__main__":
    success = run_quick_test()
    sys.exit(0 if success else 1)
