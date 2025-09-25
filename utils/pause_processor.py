import re

def add_pauses(text: str, pause_scale: int = 2) -> str:
    """
    Add characteristic Paul Graham pauses and speech patterns based on scale
    
    Args:
        text (str): Original text
        pause_scale (int): Scale from 0-5 (0=no pauses, 5=maximum pauses)
        
    Returns:
        str: Text enhanced with pause markers
    """
    if pause_scale < 0 or pause_scale > 5:
        raise ValueError("Pause scale must be between 0 and 5")
    
    if pause_scale == 0:
        return text
    
    enhanced_text = text
    
    # Scale 1: Light pauses (every 3rd sentence ending)
    if pause_scale >= 1:
        enhanced_text = add_light_pauses(enhanced_text)
    
    # Scale 2: Moderate pauses (every 2nd sentence ending) - DEFAULT
    if pause_scale >= 2:
        enhanced_text = add_moderate_pauses(enhanced_text)
    
    # Scale 3: Regular pauses (most sentence endings)
    if pause_scale >= 3:
        enhanced_text = add_regular_pauses(enhanced_text)
    
    # Scale 4: Frequent pauses (all sentence endings)
    if pause_scale >= 4:
        enhanced_text = add_frequent_pauses(enhanced_text)
    
    # Scale 5: Maximum pauses (multiple "hmm"s + longer pauses)
    if pause_scale >= 5:
        enhanced_text = add_maximum_pauses(enhanced_text)
    
    return enhanced_text

def add_light_pauses(text: str) -> str:
    """Add light pauses - every 3rd sentence ending"""
    sentences = split_sentences(text)
    result = []
    
    for i, sentence in enumerate(sentences):
        result.append(sentence)
        if (i + 1) % 3 == 0 and i < len(sentences) - 1:
            result.append(" <pause>")
    
    return "".join(result)

def add_moderate_pauses(text: str) -> str:
    """Add moderate pauses - every 2nd sentence ending"""
    sentences = split_sentences(text)
    result = []
    
    for i, sentence in enumerate(sentences):
        result.append(sentence)
        if (i + 1) % 2 == 0 and i < len(sentences) - 1:
            result.append(" Hmm.")
    
    # Add thoughtful pauses before key insights
    enhanced = "".join(result)
    enhanced = re.sub(r'\. ([A-Z][^.]*think[^.]*\.)', r'. Well, \1', enhanced)
    enhanced = re.sub(r'\. ([A-Z][^.]*important[^.]*\.)', r'. <pause> \1', enhanced)
    
    return enhanced

def add_regular_pauses(text: str) -> str:
    """Add regular pauses - most sentence endings"""
    enhanced = text
    
    # Add pauses after key transition words
    enhanced = re.sub(r'\. (But|However|So|Now|Actually)', r'. <pause> \1', enhanced)
    enhanced = re.sub(r'\. ([A-Z][^.]*because[^.]*\.)', r'. Hmm, \1', enhanced)
    
    # Add pauses before important points
    enhanced = re.sub(r'\. (The key|The important|What matters)', r'. <pause> \1', enhanced)
    
    return enhanced

def add_frequent_pauses(text: str) -> str:
    """Add frequent pauses - all sentence endings"""
    enhanced = text
    
    # Add pauses after all sentence endings
    enhanced = re.sub(r'\.(\s+[A-Z])', r'. <pause>\1', enhanced)
    
    # Add "hmm" before insights
    enhanced = re.sub(r'\. ([A-Z][^.]*insight[^.]*\.)', r'. Hmm, \1', enhanced)
    enhanced = re.sub(r'\. ([A-Z][^.]*believe[^.]*\.)', r'. You see, \1', enhanced)
    
    # Add pauses after questions
    enhanced = re.sub(r'\? ', '? <pause> ', enhanced)
    
    return enhanced

def add_maximum_pauses(text: str) -> str:
    """Add maximum pauses - multiple hmms and longer pauses"""
    enhanced = text
    
    # Multiple pauses and longer hesitations
    enhanced = re.sub(r'\.(\s+[A-Z])', r'. <long_pause>\1', enhanced)
    enhanced = re.sub(r'\? ', '? Hmm, well, ', enhanced)
    
    # Add multiple "hmm"s for emphasis
    enhanced = re.sub(r'\. ([A-Z][^.]*startup[^.]*\.)', r'. Hmm, hmm, \1', enhanced)
    enhanced = re.sub(r'\. ([A-Z][^.]*founder[^.]*\.)', r'. Well, you see, \1', enhanced)
    
    # Add thoughtful pauses mid-sentence
    enhanced = re.sub(r', (and|but|so)', r', <pause> \1', enhanced)
    
    return enhanced

def split_sentences(text: str) -> list:
    """Split text into sentences while preserving punctuation"""
    # Split on sentence boundaries but keep the punctuation
    sentences = re.split(r'([.!?]+)', text)
    
    # Rejoin punctuation with sentences
    result = []
    for i in range(0, len(sentences) - 1, 2):
        sentence = sentences[i]
        if i + 1 < len(sentences):
            sentence += sentences[i + 1]
        if sentence.strip():
            result.append(sentence)
    
    # Handle final sentence if it doesn't end with punctuation
    if len(sentences) % 2 == 1 and sentences[-1].strip():
        result.append(sentences[-1])
    
    return result

def remove_pauses(text: str) -> str:
    """Remove pause markers from text (useful for text-only output)"""
    cleaned = text
    cleaned = re.sub(r'<pause>', '', cleaned)
    cleaned = re.sub(r'<long_pause>', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Clean up extra spaces
    return cleaned.strip()

def get_pause_scale_description(scale: int) -> str:
    """Get description of what each pause scale does"""
    descriptions = {
        0: "No pauses added",
        1: "Light pauses (every 3rd sentence ending)",
        2: "Moderate pauses (every 2nd sentence ending) - DEFAULT",
        3: "Regular pauses (most sentence endings)",
        4: "Frequent pauses (all sentence endings)",
        5: "Maximum pauses (multiple 'hmm's + longer pauses)"
    }
    return descriptions.get(scale, "Invalid scale")

if __name__ == "__main__":
    # Test the pause processor
    test_text = "The best way to get startup ideas is to notice problems. So look for things that annoy you. But make sure they're problems lots of people have. This is important because you need a big market."
    
    print("Original text:")
    print(test_text)
    
    for scale in range(6):
        print(f"\nScale {scale}: {get_pause_scale_description(scale)}")
        processed = add_pauses(test_text, scale)
        print(processed)
