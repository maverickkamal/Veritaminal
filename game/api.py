"""
API module for Veritaminal

Handles interactions with the Google Gemini AI API for generating game content.
"""

import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# System instructions for different AI functionalities
SYSTEM_INSTRUCTIONS = {
    "document_generation": """
    You are a document generation system for a border control game.
    Generate realistic but fictional traveler information that could include:
    - Names from various cultures
    - Permit numbers (following specific formats)
    - Brief backstories
    
    Keep content appropriate and non-political. Occasionally include subtle inconsistencies
    that a vigilant border agent might detect.
    """,
    
    "veritas_assistant": """
    You are Veritas, an AI assistant to a border control agent.
    Your role is to:
    - Provide subtle hints about document authenticity
    - Remain neutral but observant
    - Use clear, concise language
    - Occasionally express a slight personality
    
    Avoid directly telling the player the answer. Instead, guide their attention
    to potential issues or confirmations.
    """,
    
    "narrative_generation": """
    You are crafting a branching narrative for a border control simulation game.
    Create short, engaging story fragments that:
    - Respond to player decisions
    - Gradually build tension
    - Occasionally introduce moral dilemmas
    - Maintain consistent world-building
    
    Keep text concise (25-50 words) and focused on consequences of actions.
    """
}

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("No API key found. Please set GEMINI_API_KEY in your .env file.")

client = genai.Client(api_key=api_key)


def generate_text(prompt, system_type="document_generation", max_tokens=200):
    """
    Generate text using the Google Gemini AI API.
    
    Args:
        prompt (str): The prompt to send to the API.
        system_type (str): Type of system instruction to use.
        max_tokens (int): Maximum number of tokens to generate.
        
    Returns:
        str: Generated text.
    """
    try:
        # Select the appropriate system instruction
        system_instruction = SYSTEM_INSTRUCTIONS.get(system_type, SYSTEM_INSTRUCTIONS["document_generation"])

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.9,
                system_instruction=system_instruction
            )
        )
        
        
        return response.text
            
    except Exception as e:
        logger.error("Error generating text: %s", str(e))
        return "Error generating text"

def get_veritas_hint(doc, system_type="veritas_assistant", max_tokens=100):
    """
    Get a hint from Veritas about the document.
    
    Args:
        doc (dict): The document to analyze.
        
    Returns:
        str: A hint from Veritas.
    """
    system_instruction = SYSTEM_INSTRUCTIONS.get(system_type, SYSTEM_INSTRUCTIONS["veritas_assistant"])
    prompt = f"Analyze this traveler: Name: {doc['name']}, Permit: {doc['permit']}, Backstory: {doc['backstory']}. Provide a subtle hint about document authenticity without directly revealing if it's valid or not."
    
    response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.9,
                system_instruction=system_instruction
            )
        )
        
    return response.text
    
def generate_document_error():
    """
    Generate a random error to introduce into a document.
    
    Returns:
        tuple: (error_type, error_description)
    """
    prompt = "Generate a realistic error that might appear in travel documentation. Format as: error_type: brief description"

    response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=1000,
                temperature=0.9
            )
        )
    
    return response.text
    

def generate_narrative_update(current_state, decision, is_correct):
    """
    Generate a narrative update based on player decisions.
    
    Args:
        current_state (dict): The current story state.
        decision (str): The player's decision (approve/deny).
        is_correct (bool): Whether the decision was correct.
        
    Returns:
        str: A narrative update.
    """
    corruption = current_state.get("corruption", 0)
    trust = current_state.get("trust", 0)
    
    prompt = f"""
    Player decision: {decision}
    Decision correctness: {'correct' if is_correct else 'incorrect'}
    Current corruption level: {corruption}
    Current trust level: {trust}
    
    Generate a brief narrative update (1-2 sentences) describing the consequences of this decision.
    """

    system_instruction = SYSTEM_INSTRUCTIONS.get("narrative_generation", SYSTEM_INSTRUCTIONS["narrative_generation"])

    response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=2000,
                temperature=0.9,
                system_instruction=system_instruction
            )
        )
        
    
    return response.text
