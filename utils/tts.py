import vertexai
from vertexai.generative_models import GenerativeModel
import os
import time
import re

def text_to_speech(text: str, voice_name: str = "en-US-Neural2-A", output_path: str = None) -> str:
    """
    Convert text to speech using Google's CHIRP3 model
    
    Args:
        text (str): Text to convert to speech
        voice_name (str): Voice to use (default: en-US-Neural2-A)
        output_path (str): Optional custom output path
        
    Returns:
        str: Path to generated audio file
    """
    # Initialize Vertex AI
    vertexai.init(project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="us-central1")
    
    # Add Paul Graham characteristic pauses
    enhanced_text = add_paul_graham_pauses(text)
    
    # Use CHIRP3 for text-to-speech
    model = GenerativeModel("chirp-3")
    
    # Generate speech
    response = model.generate_content(
        f"Convert this text to speech with voice {voice_name}: {enhanced_text}",
        generation_config={
            "response_mime_type": "audio/mpeg"
        }
    )
    
    # Save audio file
    if output_path is None:
        output_path = f"audio/response_{int(time.time())}.mp3"
    
    # Ensure audio directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write audio content to file
    with open(output_path, "wb") as f:
        f.write(response.parts[0].data)
    
    return output_path

def add_paul_graham_pauses(text: str) -> str:
    """
    Add characteristic Paul Graham pauses and speech patterns
    
    Args:
        text (str): Original text
        
    Returns:
        str: Enhanced text with pauses
    """
    # Add thoughtful pauses before key insights
    enhanced = text
    
    # Add "hmm" before sentences that start with insights
    enhanced = re.sub(r'\. ([A-Z][^.]*insight[^.]*\.)', r'. Hmm, \1', enhanced)
    enhanced = re.sub(r'\. ([A-Z][^.]*think[^.]*\.)', r'. Well, \1', enhanced)
    enhanced = re.sub(r'\. ([A-Z][^.]*believe[^.]*\.)', r'. You see, \1', enhanced)
    
    # Add pauses after questions
    enhanced = re.sub(r'\? ', '? Well, ', enhanced)
    
    # Add emphasis to key words
    enhanced = re.sub(r'\b(startup|founder|programming|hacker)\b', r'<emphasis>\1</emphasis>', enhanced)
    
    return enhanced

def batch_text_to_speech(texts: list[str], voice_name: str = "en-US-Neural2-A") -> list[str]:
    """
    Convert multiple texts to speech files
    
    Args:
        texts (list[str]): List of texts to convert
        voice_name (str): Voice to use
        
    Returns:
        list[str]: List of audio file paths
    """
    audio_paths = []
    
    for i, text in enumerate(texts):
        output_path = f"audio/batch_response_{int(time.time())}_{i}.mp3"
        audio_path = text_to_speech(text, voice_name, output_path)
        audio_paths.append(audio_path)
    
    return audio_paths

if __name__ == "__main__":
    # Test the TTS function
    test_text = "The best way to get startup ideas is to notice problems. Hmm, what problems do you face in your daily work?"
    
    audio_path = text_to_speech(test_text)
    print(f"Audio generated at: {audio_path}")
    
    # Test batch TTS
    test_texts = [
        "Startups are about growth.",
        "Do things that don't scale.",
        "The best way to get startup ideas is to notice problems."
    ]
    
    audio_paths = batch_text_to_speech(test_texts)
    print(f"Batch audio files: {audio_paths}")
