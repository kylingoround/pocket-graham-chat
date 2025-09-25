import os
from typing import List, Dict

def load_essays(data_directory: str, meta_dict: Dict) -> List[Dict]:
    """
    Load essay files and merge with metadata
    
    Args:
        data_directory (str): Directory containing essay text files
        meta_dict (dict): Metadata mapping from load_meta function
        
    Returns:
        List[Dict]: List of essays with enriched metadata
    """
    essays = []
    
    if not os.path.exists(data_directory):
        raise FileNotFoundError(f"Data directory not found: {data_directory}")
    
    for text_id, meta in meta_dict.items():
        filename = meta['filename']
        filepath = os.path.join(data_directory, filename)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read().strip()
                
                essay = {
                    'filename': filename,
                    'text_id': text_id,
                    'title': meta['title'],
                    'url': meta['url'],
                    'content': content
                }
                essays.append(essay)
                
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
        else:
            print(f"File not found: {filepath}")
    
    return essays

def load_single_essay(filepath: str, meta: Dict) -> Dict:
    """
    Load a single essay file with metadata
    
    Args:
        filepath (str): Path to the essay file
        meta (dict): Metadata for this essay
        
    Returns:
        Dict: Essay with enriched metadata
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Essay file not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read().strip()
    
    return {
        'filename': os.path.basename(filepath),
        'text_id': meta['text_id'],
        'title': meta['title'],
        'url': meta['url'],
        'content': content
    }

if __name__ == "__main__":
    # Test the function
    from load_meta import load_meta
    
    data_dir = "../data"
    meta_path = "../meta.csv"
    
    if os.path.exists(meta_path) and os.path.exists(data_dir):
        # Load metadata first
        meta_data = load_meta(meta_path)
        
        # Load essays
        essays = load_essays(data_dir, meta_data)
        print(f"Loaded {len(essays)} essays")
        
        # Show first essay info
        if essays:
            first_essay = essays[0]
            print(f"First essay: {first_essay['title']}")
            print(f"Content length: {len(first_essay['content'])} characters")
    else:
        print("Missing required files for testing")
