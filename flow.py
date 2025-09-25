from pocketflow import Flow
from nodes import (
    # Offline nodes
    LoadMetaNode, LoadEssaysNode, ChunkEssaysNode, EmbedChunksNode, StoreIndexNode,
    # Online nodes
    LoadIndexNode, InputQuestionNode, ValidateRelevanceNode, EmbedQueryNode,
    RetrieveChunksNode, GenerateAnswerNode, FormatResponseNode, GenerateAudioNode,
    # Special nodes
    DeclineNode
)

def create_offline_flow():
    """
    Create the offline flow for one-time essay processing and indexing
    
    This flow processes Paul Graham's essays and creates a searchable vector index:
    1. Load metadata from meta.csv
    2. Load essay content files
    3. Break essays into chunks
    4. Generate embeddings for chunks
    5. Create and save vector index
    """
    # Create offline nodes
    load_meta = LoadMetaNode()
    load_essays = LoadEssaysNode()
    chunk_essays = ChunkEssaysNode()
    embed_chunks = EmbedChunksNode()
    store_index = StoreIndexNode()
    
    # Connect nodes in sequence
    load_meta >> load_essays >> chunk_essays >> embed_chunks >> store_index
    
    return Flow(start=load_meta)

def create_online_flow():
    """
    Create the online flow for real-time user Q&A with RAG
    
    This flow handles user questions using the pre-built index:
    1. Load pre-built vector index
    2. Get user question
    3. Validate question relevance
    4. Embed question (if relevant)
    5. Retrieve relevant chunks
    6. Generate Paul Graham-style answer
    7. Format response with citations
    8. Generate audio with pauses
    """
    # Create online nodes
    load_index = LoadIndexNode()
    input_question = InputQuestionNode()
    validate_relevance = ValidateRelevanceNode()
    embed_query = EmbedQueryNode()
    retrieve_chunks = RetrieveChunksNode()
    generate_answer = GenerateAnswerNode()
    format_response = FormatResponseNode()
    generate_audio = GenerateAudioNode()
    decline = DeclineNode()
    
    # Connect nodes with branching based on relevance validation
    load_index >> input_question >> validate_relevance
    
    # Relevant questions go through the full RAG pipeline
    validate_relevance - "relevant" >> embed_query >> retrieve_chunks >> generate_answer >> format_response >> generate_audio
    
    # Irrelevant questions go to decline handler
    validate_relevance - "decline" >> decline
    
    return Flow(start=load_index)

def create_continuous_qa_flow():
    """
    Create a flow that can handle multiple questions in a loop
    This loads the index once and then processes questions continuously
    """
    load_index = LoadIndexNode()
    input_question = InputQuestionNode()
    validate_relevance = ValidateRelevanceNode()
    embed_query = EmbedQueryNode()
    retrieve_chunks = RetrieveChunksNode()
    generate_answer = GenerateAnswerNode()
    format_response = FormatResponseNode()
    generate_audio = GenerateAudioNode()
    decline = DeclineNode()
    
    # Connect with loop back to input for continuous questioning
    load_index >> input_question
    input_question >> validate_relevance
    
    # Relevant questions
    validate_relevance - "relevant" >> embed_query >> retrieve_chunks >> generate_answer >> format_response >> generate_audio >> input_question
    
    # Irrelevant questions
    validate_relevance - "decline" >> decline >> input_question
    
    return Flow(start=load_index)