from typing import List, Dict
import re

def chunk_text(essay: Dict, chunk_size: int = 500, overlap: int = 100) -> List[Dict]:
    """
    Break essay into contextual chunks with citation metadata
    
    Args:
        essay (Dict): Essay with metadata (from file_loader)
        chunk_size (int): Target size for each chunk
        overlap (int): Overlap between consecutive chunks
        
    Returns:
        List[Dict]: List of chunks with citation metadata
    """
    content = essay['content']
    chunks = []
    
    # Split into sentences for better chunk boundaries
    sentences = split_into_sentences(content)
    
    current_chunk = ""
    current_pos = 0
    chunk_index = 0
    
    for sentence in sentences:
        # If adding this sentence would exceed chunk_size and we have content
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            # Create chunk
            chunk = create_chunk(
                text=current_chunk.strip(),
                essay=essay,
                chunk_index=chunk_index,
                start_pos=current_pos,
                end_pos=current_pos + len(current_chunk)
            )
            chunks.append(chunk)
            
            # Start new chunk with overlap
            overlap_text = get_overlap_text(current_chunk, overlap)
            current_chunk = overlap_text + sentence
            current_pos += len(current_chunk) - len(overlap_text)
            chunk_index += 1
        else:
            current_chunk += sentence
    
    # Handle remaining content
    if current_chunk.strip():
        chunk = create_chunk(
            text=current_chunk.strip(),
            essay=essay,
            chunk_index=chunk_index,
            start_pos=current_pos,
            end_pos=current_pos + len(current_chunk)
        )
        chunks.append(chunk)
    
    return chunks

def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using basic sentence boundaries
    
    Args:
        text (str): Input text
        
    Returns:
        List[str]: List of sentences
    """
    # Split on sentence endings, but keep the punctuation
    sentences = re.split(r'([.!?]+\s+)', text)
    
    # Rejoin punctuation with sentences
    result = []
    for i in range(0, len(sentences) - 1, 2):
        sentence = sentences[i]
        if i + 1 < len(sentences):
            sentence += sentences[i + 1]
        if sentence.strip():
            result.append(sentence)
    
    # Handle case where text doesn't end with sentence punctuation
    if sentences and not sentences[-1].strip() == '':
        last_part = sentences[-1]
        if last_part.strip():
            result.append(last_part)
    
    return result

def get_overlap_text(text: str, overlap_size: int) -> str:
    """
    Get the last overlap_size characters for chunk overlap
    
    Args:
        text (str): Source text
        overlap_size (int): Number of characters to overlap
        
    Returns:
        str: Overlap text
    """
    if len(text) <= overlap_size:
        return text
    
    # Try to break at word boundary
    overlap_text = text[-overlap_size:]
    space_index = overlap_text.find(' ')
    
    if space_index > 0:
        return overlap_text[space_index:]
    else:
        return overlap_text

def create_chunk(text: str, essay: Dict, chunk_index: int, start_pos: int, end_pos: int) -> Dict:
    """
    Create a chunk dictionary with all metadata
    
    Args:
        text (str): Chunk text content
        essay (Dict): Source essay metadata
        chunk_index (int): Index of this chunk in the essay
        start_pos (int): Start position in original text
        end_pos (int): End position in original text
        
    Returns:
        Dict: Chunk with citation metadata
    """
    return {
        'text': text,
        'essay_title': essay['title'],
        'essay_filename': essay['filename'],
        'essay_url': essay['url'],
        'text_id': essay['text_id'],
        'chunk_index': chunk_index,
        'start_pos': start_pos,
        'end_pos': end_pos,
        'embedding': []  # Will be populated during embedding phase
    }

if __name__ == "__main__":
    # Test the chunking function
    test_essay = {
        'filename': 'test.txt',
        'text_id': '1',
        'title': 'Test Essay',
        'url': 'http://example.com/test',
        'content': "This is the first sentence. This is the second sentence with more content to make it longer. This is the third sentence. And this is the fourth sentence with even more content to demonstrate chunking behavior."
    }
    
    chunks = chunk_text(test_essay, chunk_size=100, overlap=20)
    
    print(f"Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i}:")
        print(f"Text: {chunk['text'][:100]}...")
        print(f"Length: {len(chunk['text'])}")
        print(f"Positions: {chunk['start_pos']}-{chunk['end_pos']}")
