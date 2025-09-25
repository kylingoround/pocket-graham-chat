from pocketflow import Node, BatchNode
from utils.call_llm import call_llm
from utils.load_meta import load_meta
from utils.file_loader import load_essays
from utils.chunking import chunk_text
from utils.get_embedding import get_embedding, batch_get_embeddings
from utils.vector_db import create_vector_index, load_vector_index, search_vector_index
from utils.validate_relevance import validate_question_relevance, get_suggested_questions
from utils.pause_processor import add_pauses
from utils.tts import text_to_speech
import os

# ============================================================================
# OFFLINE FLOW NODES (One-time Setup)
# ============================================================================

class LoadMetaNode(Node):
    """Read essay metadata from meta.csv"""
    
    def prep(self, shared):
        return shared["config"]["meta_csv"]
    
    def exec(self, meta_csv_path):
        return load_meta(meta_csv_path)
    
    def post(self, shared, prep_res, exec_res):
        shared["meta_dict"] = exec_res
        print(f"Loaded metadata for {len(exec_res)} essays")
        return "default"

class LoadEssaysNode(BatchNode):
    """Read essay files and merge with metadata"""
    
    def prep(self, shared):
        data_dir = shared["config"]["data_dir"]
        meta_dict = shared["meta_dict"]
        
        # Return list of (filepath, metadata) tuples for batch processing
        items = []
        for text_id, meta in meta_dict.items():
            filepath = os.path.join(data_dir, meta["filename"])
            items.append((filepath, meta))
        
        return items
    
    def exec(self, item):
        filepath, meta = item
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            
            return {
                'filename': meta['filename'],
                'text_id': meta['text_id'],
                'title': meta['title'],
                'url': meta['url'],
                'content': content
            }
        else:
            print(f"Warning: File not found: {filepath}")
            return None
    
    def post(self, shared, prep_res, exec_res_list):
        # Filter out None results and store essays
        essays = [essay for essay in exec_res_list if essay is not None]
        shared["essays"] = essays
        print(f"Loaded {len(essays)} essays successfully")
        return "default"

class ChunkEssaysNode(BatchNode):
    """Break essays into contextual chunks with citation metadata"""
    
    def prep(self, shared):
        chunk_size = shared.get("config", {}).get("chunk_size", 500)
        chunk_overlap = shared.get("config", {}).get("chunk_overlap", 100)
        return [
            (essay, chunk_size, chunk_overlap)
            for essay in shared["essays"]
        ]
    
    def exec(self, item):
        essay, chunk_size, chunk_overlap = item
        return chunk_text(essay, chunk_size, chunk_overlap)
    
    def post(self, shared, prep_res, exec_res_list):
        # Flatten all chunks into a single list
        all_chunks = []
        for chunk_list in exec_res_list:
            all_chunks.extend(chunk_list)
        
        shared["chunks"] = all_chunks
        print(f"Created {len(all_chunks)} chunks from {len(exec_res_list)} essays")
        return "default"

class EmbedChunksNode(BatchNode):
    """Create vector embeddings for all chunks"""
    
    def prep(self, shared):
        chunks = shared["chunks"]
        return [chunk["text"] for chunk in chunks]
    
    def exec(self, chunk_text):
        return get_embedding(chunk_text)
    
    def post(self, shared, prep_res, exec_res_list):
        # Store embeddings and update chunks with embeddings
        chunks = shared["chunks"]
        for i, embedding in enumerate(exec_res_list):
            if i < len(chunks):
                chunks[i]["embedding"] = embedding
        
        shared["embeddings"] = exec_res_list
        print(f"Generated embeddings for {len(exec_res_list)} chunks")
        return "default"

class StoreIndexNode(Node):
    """Create and save vector database index"""
    
    def prep(self, shared):
        return shared["embeddings"], shared["chunks"]
    
    def exec(self, inputs):
        embeddings, chunks = inputs
        return create_vector_index(embeddings, chunks)
    
    def post(self, shared, prep_res, exec_res):
        shared["vector_index"] = exec_res
        
        # Save to persistent storage
        index_path = shared["config"]["index_path"]
        exec_res.save(index_path)
        print(f"Vector index saved to {index_path}")
        return "default"

# ============================================================================
# ONLINE FLOW NODES (Real-time User Interaction)
# ============================================================================

class LoadIndexNode(Node):
    """Load pre-built vector index from persistent storage"""
    
    def prep(self, shared):
        return shared["config"]["index_path"]
    
    def exec(self, index_path):
        return load_vector_index(index_path)
    
    def post(self, shared, prep_res, exec_res):
        vector_index, chunks_metadata = exec_res
        shared["vector_index"] = vector_index
        shared["chunks_metadata"] = chunks_metadata
        print(f"Loaded vector index with {len(chunks_metadata)} chunks")
        return "default"

class InputQuestionNode(Node):
    """Capture and store user question"""
    
    def exec(self, _):
        return input("\nEnter your question about Paul Graham's essays: ")
    
    def post(self, shared, prep_res, exec_res):
        shared["user_question"] = exec_res.strip()
        return "default"

class ValidateRelevanceNode(Node):
    """Check if question relates to Paul Graham's expertise"""
    
    def prep(self, shared):
        return shared["user_question"]
    
    def exec(self, question):
        return validate_question_relevance(question)
    
    def post(self, shared, prep_res, exec_res):
        is_relevant, decline_reason = exec_res
        shared["is_relevant"] = is_relevant
        shared["decline_reason"] = decline_reason
        
        if is_relevant:
            return "relevant"
        else:
            print(f"\n{decline_reason}")
            print("\nHere are some questions you might try instead:")
            for question in get_suggested_questions()[:3]:
                print(f"• {question}")
            return "decline"

class EmbedQueryNode(Node):
    """Convert user question to vector embedding"""
    
    def prep(self, shared):
        return shared["user_question"]
    
    def exec(self, question):
        return get_embedding(question)
    
    def post(self, shared, prep_res, exec_res):
        shared["query_embedding"] = exec_res
        return "default"

class RetrieveChunksNode(Node):
    """Find top most relevant chunks with citation info"""
    
    def prep(self, shared):
        query_embedding = shared["query_embedding"]
        vector_index = shared["vector_index"]
        max_chunks = shared["config"]["max_chunks"]
        return query_embedding, vector_index, max_chunks
    
    def exec(self, inputs):
        query_embedding, vector_index, max_chunks = inputs
        return search_vector_index(query_embedding, vector_index, top_k=max_chunks)
    
    def post(self, shared, prep_res, exec_res):
        shared["retrieved_chunks"] = exec_res
        print(f"Retrieved {len(exec_res)} relevant chunks")
        return "default"

class GenerateAnswerNode(Node):
    """Create Paul Graham-style response using retrieved context"""
    
    def prep(self, shared):
        question = shared["user_question"]
        chunks = shared["retrieved_chunks"]
        return question, chunks
    
    def exec(self, inputs):
        question, chunks = inputs
        
        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(chunks):
            context_parts.append(f"Source {i+1} (from '{chunk['essay_title']}'):\n{chunk['text']}")
        
        context = "\n\n".join(context_parts)
        
        # Create Paul Graham-style prompt
        prompt = f"""You are Paul Graham. Answer this question using only the provided context from your essays. 

Keep your response under 50 words and use your characteristic style:
- Direct and insightful
- Use simple, clear language  
- Focus on practical wisdom
- Be opinionated but thoughtful

Context from your essays:
{context}

Question: {question}

Answer briefly in Paul Graham's voice:"""
        
        return call_llm(prompt)
    
    def post(self, shared, prep_res, exec_res):
        shared["generated_answer"] = exec_res.strip()
        return "default"

class FormatResponseNode(Node):
    """Add source citations and prepare final text output"""
    
    def prep(self, shared):
        answer = shared["generated_answer"]
        chunks = shared["retrieved_chunks"]
        return answer, chunks
    
    def exec(self, inputs):
        answer, chunks = inputs
        
        # Create citations
        citations = []
        for i, chunk in enumerate(chunks):
            citation = {
                "citation_id": f"cite_{i+1}",
                "essay_title": chunk["essay_title"],
                "essay_url": chunk["essay_url"],
                "chunk_text": chunk["text"][:100] + "..." if len(chunk["text"]) > 100 else chunk["text"],
                "relevance_score": chunk["similarity_score"]
            }
            citations.append(citation)
        
        # Format text with citations
        formatted_text = f"{answer}\n\nSources:"
        for citation in citations:
            formatted_text += f"\n• {citation['essay_title']} (relevance: {citation['relevance_score']:.2f})"
        
        return formatted_text, citations
    
    def post(self, shared, prep_res, exec_res):
        formatted_text, citations = exec_res
        shared["formatted_response"] = {
            "text": formatted_text,
            "citations": citations,
            "audio_path": ""
        }
        return "default"

class GenerateAudioNode(Node):
    """Create TTS audio with scaled 'hmm' pauses"""
    
    def prep(self, shared):
        text = shared["generated_answer"]  # Use just the answer for audio
        pause_scale = shared["config"]["pause_scale"]
        return text, pause_scale
    
    def exec(self, inputs):
        text, pause_scale = inputs
        
        # Add pauses based on scale
        text_with_pauses = add_pauses(text, pause_scale)
        
        # Generate audio
        audio_path = text_to_speech(text_with_pauses)
        
        return audio_path
    
    def post(self, shared, prep_res, exec_res):
        shared["formatted_response"]["audio_path"] = exec_res
        print(f"Audio generated: {exec_res}")
        return "default"

# ============================================================================
# DECLINE FLOW NODE
# ============================================================================

class DeclineNode(Node):
    """Handle declined questions with polite message"""
    
    def exec(self, _):
        return "Question declined - see validation message above"
    
    def post(self, shared, prep_res, exec_res):
        # Clear any partial processing
        shared["generated_answer"] = ""
        shared["formatted_response"] = {
            "text": shared.get("decline_reason", "Sorry, I can't help with that question."),
            "citations": [],
            "audio_path": ""
        }
        return "default"
