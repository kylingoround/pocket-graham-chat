from utils.call_llm import call_llm
import re

def validate_question_relevance(question: str) -> tuple:
    """
    Validate if a question relates to Paul Graham's expertise areas
    
    Args:
        question (str): User's question
        
    Returns:
        tuple[bool, str]: (is_relevant, reason/decline_message)
    """
    # Quick keyword-based pre-filtering for obviously relevant topics
    relevant_keywords = [
        'startup', 'startups', 'entrepreneur', 'entrepreneurship', 'founder', 'founders',
        'programming', 'coding', 'software', 'development', 'technology', 'tech',
        'business', 'company', 'venture', 'investment', 'investor',
        'essay', 'writing', 'communication', 'education', 'learning',
        'hacker', 'hackers', 'lisp', 'arc', 'y combinator', 'ycombinator',
        'innovation', 'growth', 'scale', 'scaling', 'productivity'
    ]
    
    # Quick keyword-based pre-filtering for obviously irrelevant topics
    irrelevant_keywords = [
        'medical', 'health', 'doctor', 'medicine', 'treatment', 'diagnosis',
        'legal', 'law', 'lawyer', 'attorney', 'lawsuit', 'court',
        'personal', 'private', 'family', 'relationship', 'dating',
        'current', 'news', 'politics', 'political', 'election', 'government',
        'support', 'help', 'fix', 'troubleshoot', 'install', 'download'
    ]
    
    question_lower = question.lower()
    
    # Check for obviously irrelevant topics
    for keyword in irrelevant_keywords:
        if keyword in question_lower:
            return False, f"I focus on topics like startups, programming, and essays rather than {keyword}-related questions. Try asking about entrepreneurship, technology, or writing instead."
    
    # Check for obviously relevant topics
    for keyword in relevant_keywords:
        if keyword in question_lower:
            return True, ""
    
    # Use LLM for more nuanced validation
    return llm_validate_relevance(question)

def llm_validate_relevance(question: str) -> tuple:
    """
    Use LLM to validate question relevance with more nuance
    
    Args:
        question (str): User's question
        
    Returns:
        tuple[bool, str]: (is_relevant, reason/decline_message)
    """
    prompt = f"""
You are helping filter questions for a Paul Graham chatbot. Paul Graham is known for:
- Startups and entrepreneurship
- Programming (especially Lisp)
- Essays and writing
- Y Combinator and investing
- Technology and innovation
- Education and learning
- Productivity and decision-making

Question: "{question}"

Is this question relevant to Paul Graham's expertise? Respond in this format:

```yaml
relevant: true/false
reason: brief explanation
decline_message: polite message if not relevant (or empty if relevant)
```"""

    try:
        response = call_llm(prompt)
        
        # Extract YAML content
        yaml_match = re.search(r'```yaml\s*(.*?)\s*```', response, re.DOTALL)
        if not yaml_match:
            # Fallback: assume relevant if can't parse
            return True, ""
        
        yaml_content = yaml_match.group(1)
        
        # Simple YAML parsing (since it's structured)
        relevant = "true" in yaml_content.lower().split("relevant:")[1].split("\n")[0]
        
        if relevant:
            return True, ""
        else:
            # Extract decline message
            try:
                decline_line = [line for line in yaml_content.split('\n') if 'decline_message:' in line][0]
                decline_message = decline_line.split('decline_message:')[1].strip()
                return False, decline_message
            except:
                return False, "I focus on topics like startups, programming, and essays. Could you ask about one of those areas instead?"
    
    except Exception as e:
        print(f"Error in LLM validation: {e}")
        # Fallback: assume relevant if LLM fails
        return True, ""

def get_suggested_questions() -> list[str]:
    """
    Get suggested questions to help users ask relevant queries
    
    Returns:
        list[str]: List of suggested questions
    """
    return [
        "How do I come up with good startup ideas?",
        "What makes a successful founder?",
        "How should early-stage startups approach growth?",
        "What programming languages should I learn?",
        "How do I write better essays?",
        "What should I look for when choosing co-founders?",
        "How do I know if my startup idea is worth pursuing?",
        "What mistakes do first-time entrepreneurs make?",
        "How important is technical skill for startup founders?",
        "What advice would you give to someone learning to program?"
    ]

if __name__ == "__main__":
    # Test the validation function
    test_questions = [
        "How do I get startup ideas?",  # Should be relevant
        "What programming language should I learn?",  # Should be relevant
        "How do I treat my flu?",  # Should be irrelevant
        "What's the best way to scale a business?",  # Should be relevant
        "How do I fix my computer?",  # Should be irrelevant
        "What makes good writing?"  # Should be relevant
    ]
    
    print("Testing question validation:")
    for question in test_questions:
        is_relevant, message = validate_question_relevance(question)
        print(f"\nQuestion: {question}")
        print(f"Relevant: {is_relevant}")
        if message:
            print(f"Message: {message}")
    
    print("\nSuggested questions:")
    for q in get_suggested_questions()[:3]:
        print(f"- {q}")
