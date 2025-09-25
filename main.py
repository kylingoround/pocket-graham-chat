from flow import create_offline_flow, create_online_flow, create_continuous_qa_flow
import os
import sys
import argparse
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Load environment variables from .env file if available
if load_dotenv is not None:
    env_override = os.getenv("POCKET_GRAHAM_ENV_FILE")
    default_env = Path(__file__).resolve().parent / ".env"
    env_path = Path(env_override).expanduser() if env_override else default_env
    load_dotenv(env_path)

def create_shared_store():
    """Create the shared store with default configuration"""
    return {
        # Configuration
        "config": {
            "data_dir": "./data",
            "meta_csv": "./meta.csv",
            "index_path": "./vector_index.pkl",  # Persistent storage location
            "pause_scale": 2,           # TTS pause scale (0-5)
            "max_chunks": 5,            # Number of chunks to retrieve
            "chunk_size": 500,          # Text chunk size
            "chunk_overlap": 100        # Overlap between chunks
        },

        # Offline Processing Data (One-time Setup)
        "meta_dict": {},                # Essay metadata from CSV
        "essays": [],                   # Essays with metadata
        "chunks": [],                   # Text chunks with citation info
        "embeddings": [],               # Vector embeddings (paired with chunks)
        "vector_index": None,           # Searchable vector index

        # Online Processing Data (Per User Question)
        "chunks_metadata": [],          # Loaded chunk metadata (from Load Index)
        "user_question": "",            # Current user question
        "is_relevant": False,           # Question relevance validation result
        "decline_reason": "",           # Reason if question declined
        "query_embedding": [],          # Question vector embedding
        "retrieved_chunks": [],         # Top chunks with similarity scores
        "generated_answer": "",         # Raw LLM response
        "text_with_pauses": "",         # Text processed with pause markers
        "formatted_response": {         # Final formatted output
            "text": "",                 # Text with citations and tooltips
            "citations": [],            # Source references for tooltips
            "audio_path": ""            # TTS audio file path
        }
    }

def run_offline_indexing():
    """Run the offline flow to process essays and create the vector index"""
    print("🔄 Starting offline indexing process...")
    print("This will process all Paul Graham essays and create a searchable index.")
    
    # Create shared store
    shared = create_shared_store()
    
    # Validate required files exist
    if not os.path.exists(shared["config"]["meta_csv"]):
        print(f"❌ Error: Meta CSV file not found at {shared['config']['meta_csv']}")
        return False
    
    if not os.path.exists(shared["config"]["data_dir"]):
        print(f"❌ Error: Data directory not found at {shared['config']['data_dir']}")
        return False
    
    try:
        # Create and run offline flow
        offline_flow = create_offline_flow()
        offline_flow.run(shared)
        
        print("✅ Offline indexing completed successfully!")
        print(f"📊 Processed {len(shared.get('essays', []))} essays")
        print(f"📋 Created {len(shared.get('chunks', []))} chunks")
        print(f"💾 Vector index saved to {shared['config']['index_path']}")
        return True
        
    except Exception as e:
        print(f"❌ Error during offline indexing: {e}")
        return False

def run_online_chat():
    """Run the online flow for real-time Q&A"""
    print("💬 Starting Paul Graham AI Assistant...")
    
    # Create shared store
    shared = create_shared_store()
    
    # Validate index exists
    if not os.path.exists(shared["config"]["index_path"]):
        print(f"❌ Error: Vector index not found at {shared['config']['index_path']}")
        print("📝 Please run offline indexing first with: python main.py --mode offline")
        return False
    
    try:
        # Create and run online flow
        online_flow = create_online_flow()
        online_flow.run(shared)
        
        # Display results
        response = shared.get("formatted_response", {})
        print("\n" + "="*60)
        print("📝 RESPONSE:")
        print(response.get("text", "No response generated"))
        
        if response.get("audio_path"):
            print(f"\n🔊 Audio: {response['audio_path']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during online chat: {e}")
        return False

def run_continuous_chat():
    """Run continuous Q&A session"""
    print("💬 Starting continuous Paul Graham AI Assistant...")
    print("Type 'quit' or 'exit' to stop.\n")
    
    # Create shared store
    shared = create_shared_store()
    
    # Validate index exists
    if not os.path.exists(shared["config"]["index_path"]):
        print(f"❌ Error: Vector index not found at {shared['config']['index_path']}")
        print("📝 Please run offline indexing first with: python main.py --mode offline")
        return False
    
    # Load the index once
    from nodes import LoadIndexNode
    load_index = LoadIndexNode()
    try:
        load_index.run(shared)
        print("✅ Vector index loaded successfully!\n")
    except Exception as e:
        print(f"❌ Error loading index: {e}")
        return False
    
    # Main chat loop
    while True:
        try:
            print("-" * 40)
            question = input("\n🤔 Ask Paul Graham: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            # Process the question
            shared["user_question"] = question
            
            # Run the Q&A pipeline (skipping index loading)
            from flow import create_online_flow
            from nodes import (InputQuestionNode, ValidateRelevanceNode, EmbedQueryNode,
                             RetrieveChunksNode, GenerateAnswerNode, FormatResponseNode, 
                             GenerateAudioNode, DeclineNode)
            
            # Create nodes for this question
            validate_relevance = ValidateRelevanceNode()
            
            # Validate relevance
            validate_result = validate_relevance.run(shared)
            
            if validate_result == "relevant":
                # Process relevant question
                embed_query = EmbedQueryNode()
                retrieve_chunks = RetrieveChunksNode()
                generate_answer = GenerateAnswerNode()
                format_response = FormatResponseNode()
                
                embed_query.run(shared)
                retrieve_chunks.run(shared)
                generate_answer.run(shared)
                format_response.run(shared)
                
                # Optional: Generate audio (comment out if too slow)
                # generate_audio = GenerateAudioNode()
                # generate_audio.run(shared)
                
                # Display results
                response = shared.get("formatted_response", {})
                print("\n💡 Paul Graham says:")
                print(response.get("text", "No response generated"))
            
            else:
                # Handle declined question - message already shown by validation
                pass
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

def main():
    parser = argparse.ArgumentParser(description="Paul Graham AI Assistant")
    parser.add_argument(
        "--mode", 
        choices=["offline", "online", "continuous"],
        default="continuous",
        help="Mode to run: offline (indexing), online (single Q&A), continuous (chat loop)"
    )
    parser.add_argument(
        "--pause-scale",
        type=int,
        default=2,
        choices=range(6),
        help="TTS pause scale 0-5 (0=no pauses, 5=maximum pauses)"
    )
    
    args = parser.parse_args()
    
    print("🤖 Paul Graham AI Assistant")
    print("=" * 50)
    
    # Set pause scale if provided
    if hasattr(args, 'pause_scale'):
        # This would be set in shared config, but for simplicity we'll note it
        print(f"🔊 TTS pause scale: {args.pause_scale}")
    
    if args.mode == "offline":
        success = run_offline_indexing()
        if success:
            print("\n✨ You can now run online mode with: python main.py --mode online")
            print("   Or start continuous chat with: python main.py --mode continuous")
    
    elif args.mode == "online":
        run_online_chat()
    
    elif args.mode == "continuous":
        run_continuous_chat()

if __name__ == "__main__":
    main()
