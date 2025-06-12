from langchain_google_genai import ChatGoogleGenerativeAI
from config import settings

_llm_instance = None # Private, module-level variable to hold the instance

def get_llm() -> ChatGoogleGenerativeAI:
    """
    Returns a singleton instance of the ChatGoogleGenerativeAI model.
    """
    global _llm_instance

    # This is the core of the pattern: only create the object if it
    # doesn't already exist.
    if _llm_instance is None:
        print("--- Initializing LLM for the first time... ---")
        
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please make sure it's set in your .env file "
                "and that the file is in your project's root directory."
            )
        
        _llm_instance = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key
        )
    
    return _llm_instance
