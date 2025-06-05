from typing import List, Dict
import json
from google import genai
from google.genai import types

# Configure Gemini API
client = genai.Client(
    api_key="AIzaSyDkABqukRgGTkANcPd_AiSu23DjGhJqqfs",
)

def load_knowledge_base(jsonl_file: str) -> List[Dict]:
    """
    Load knowledge base from JSONL file containing labels and data.
    """
    knowledge_base = []
    with open(jsonl_file, 'r', encoding="utf8") as f:
        for line in f:
            item = json.loads(line)
            knowledge_base.append(item)
    return knowledge_base

def search_relevant_docs(query: str, knowledge_base: List[Dict]) -> List[str]:
    """
    Search knowledge base for relevant documents based on query and labels.
    Basic implementation - could be enhanced with better search.
    """
    relevant_docs = []
    for doc in knowledge_base:
        # Check if any labels match keywords in query
        relevant_docs.append(doc['text'])
    return relevant_docs

def get_gemini_response(history: List[Dict[str, str]], knowledge_base: List[Dict]) -> str:
    """
    Generate a response using Gemini based on conversation history and knowledge base.
    """
    try:
        # Format conversation history for Gemini
        formatted_history = ""
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted_history += f"{role}: {msg['text']}\n"
        
        # Get relevant documents based on last user query
        last_query = history[-1]['text'] if history else ""
        relevant_docs = search_relevant_docs(last_query, knowledge_base)
        context = "\n".join(relevant_docs)
        
        # Add prompt prefix with context
        prompt = f"""אתה עוזר AI שעונה רק על בסיס המידע שניתן לך. אתה עונה רק בעברית.

כללים חשובים:
1. אם המידע לא נמצא בהקשר שניתן לך - אתה חייב לענות: "אין לי את המידע הזה. אני מציע לפנות למחלקה הרלוונטית לקבלת מידע נוסף."
2. אתה עונה אך ורק על בסיס המידע שניתן לך בהקשר
3. אתה עונה רק בעברית
4. אתה לא ממציא או משלים מידע שלא קיים בהקשר
5. אם המשתמש משתף קושי או בעיה הקשורה למידע שיש לך - הבע אמפתיה והבנה לפני שתענה על השאלה

הקשר:
{context}

שיחה קודמת:
{formatted_history}
Assistant:"""

        # Generate response
        model = "gemini-2.0-flash"
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        ]
        response = client.models.generate_content(model=model, contents=contents)

        # Check if response has safety issues

        return response.text

    except Exception as e:
        print(f"Error generating Gemini response: {str(e)}")
        return "I apologize, but I encountered an error processing your request."

def generate_reply(history: List[Dict[str, str]]) -> str:
    """
    Generate reply based on conversation history using Gemini.
    """
    if not history:
        return "Hello! How can I help you today?"
    
    # Load knowledge base
    knowledge_base = load_knowledge_base('knowledge.jsonl')
    return get_gemini_response(history, knowledge_base)

# Example usage
# if __name__ == "__main__":
#     # Simulate a conversation
#     conversation = [
#         {"role": "user", "text": "What can you tell me about machine learning?"},
#         {"role": "bot", "text": "Machine learning is a branch of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed."},
#         {"role": "user", "text": "How does supervised learning work?"}
#     ]
    
#     # Generate a reply
#     response = generate_reply(conversation)
#     print("\nExample conversation:")
#     for message in conversation:
#         print(f"{message['role'].title()}: {message['text']}")
#     print(f"\nGenerated Reply: {response}")

