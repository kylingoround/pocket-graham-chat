import os
from anthropic import Anthropic

# Learn more about calling the LLM: https://the-pocket.github.io/PocketFlow/utility_function/llm.html
def call_llm(prompt):    
    # Use direct Anthropic API (not Vertex AI)
    api_key = os.environ["ANTHROPIC_API_KEY"]
    # Clean any Unicode characters that might have been copied incorrectly
    api_key = api_key.encode('ascii', 'ignore').decode('ascii')
    
    client = Anthropic(
        api_key=api_key
    )
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # Latest Claude 3.5 Sonnet
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    
    return response.content[0].text
    
if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    print(call_llm(prompt))
