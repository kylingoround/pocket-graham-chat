import csv
import os

def load_meta(meta_csv_path: str) -> dict:
    """
    Load essay metadata from meta.csv file
    
    Args:
        meta_csv_path (str): Path to the meta.csv file
        
    Returns:
        dict: Mapping of text_id to metadata dict
    """
    meta_dict = {}
    
    if not os.path.exists(meta_csv_path):
        raise FileNotFoundError(f"Meta CSV file not found: {meta_csv_path}")
    
    with open(meta_csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            text_id = row['text_id']
            meta_dict[text_id] = {
                'text_id': text_id,
                'title': row['title'],
                'url': row['link'],
                'filename': f"{text_id}.txt"
            }
    
    return meta_dict

if __name__ == "__main__":
    # Test the function
    meta_path = "../meta.csv"
    if os.path.exists(meta_path):
        meta_data = load_meta(meta_path)
        print(f"Loaded metadata for {len(meta_data)} essays")
        # Show first few entries
        for i, (text_id, meta) in enumerate(meta_data.items()):
            if i < 3:
                print(f"ID {text_id}: {meta['title']}")
    else:
        print(f"Meta file not found at {meta_path}")
