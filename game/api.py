"""
API module for Veritaminal

Handles interactions with the Google Gemini AI API for generating game content.
"""

import os
import logging
import random
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
    """,
    
    "ai_judgment": """
    You are an expert document verification system evaluating border crossing documents.
    Consider:
    - Document completeness and accuracy
    - Consistency between name, permit, and backstory
    - Compliance with current border rules and regulations
    - Subtle discrepancies that might indicate fraud
    - Political and social context of the border situation
    - Previous patterns in approval/denial decisions

    Provide a fair and nuanced evaluation.
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
            model="gemini-2.0-flash",
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

def generate_document_for_setting(setting, system_type="document_generation", max_tokens=200):
    """
    Generate a document tailored to a specific border setting.
    
    Args:
        setting (dict): The border setting to generate a document for.
        
    Returns:
        tuple: (name, permit, backstory, additional_fields)
    """
    context = f"""
    Border Setting: {setting['name']}
    Situation: {setting['situation']}
    
    Generate a traveler document for someone crossing this border.
    Include:
    1. Full name (first and last name)
    2. Permit number (format: P followed by 4 digits)
    3. A one-sentence backstory relevant to this border situation
    4. Any additional relevant fields for this specific border (e.g., visa type, purpose)
    
    Format as JSON with fields: name, permit, backstory, additional_fields
    """
    
    try:
        response_text = generate_text(context, system_type, max_tokens)
        
        # Basic parsing of the response - in a real implementation, you'd want better JSON handling
        # For this example, we'll just extract the key fields
        
        # Fallback values in case parsing fails
        name = generate_text("Generate a unique traveler name", "document_generation")
        permit = generate_text("Generate a permit number starting with 'P' followed by 4 digits", "document_generation")
        backstory = generate_consistent_backstory(name, "document_generation")
        additional_fields = {}
        
        # Try to extract fields from the response
        if "name" in response_text and "permit" in response_text:
            # Very basic extraction - not robust
            try:
                import json
                # Find JSON-like content and parse it
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                if start > -1 and end > start:
                    json_data = json.loads(response_text[start:end])
                    name = json_data.get("name", name)
                    permit = json_data.get("permit", permit)
                    backstory = json_data.get("backstory", backstory)
                    additional_fields = json_data.get("additional_fields", {})
            except:
                logger.error("Failed to parse JSON response, using fallback values")
                
        return name, permit, backstory, additional_fields
        
    except Exception as e:
        logger.error(f"Error generating document for setting: {e}")
        # Return fallback values
        name = generate_text("Generate a unique traveler name", "document_generation")
        permit = generate_text("Generate a permit number starting with 'P' followed by 4 digits", "document_generation")
        backstory = generate_consistent_backstory(name, "document_generation")
        return name, permit, backstory, {}

def generate_consistent_backstory(name, system_type="document_generation", max_tokens=100):
    """
    Generate a backstory that is consistent with the provided name.
    
    Args:
        name (str): The traveler's name to use in the backstory.
        
    Returns:
        str: A one-sentence backstory that uses the same name.
    """
    system_instruction = SYSTEM_INSTRUCTIONS.get(system_type, SYSTEM_INSTRUCTIONS["document_generation"])
    prompt = f"Create a one-sentence backstory for a traveler named {name}. Make sure to use the exact name '{name}' in the backstory."
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.9,
                system_instruction=system_instruction
            )
        )
        
        return response.text
    except Exception as e:
        logger.error("Error generating backstory: %s", str(e))
        return f"{name} is a traveler with no additional information available."

def get_veritas_hint(doc, memory_context="", system_type="veritas_assistant", max_tokens=100):
    """
    Get a hint from Veritas about the document.
    
    Args:
        doc (dict): The document to analyze.
        memory_context (str): Context from the memory manager.
        
    Returns:
        str: A hint from Veritas.
    """
    system_instruction = SYSTEM_INSTRUCTIONS.get(system_type, SYSTEM_INSTRUCTIONS["veritas_assistant"])
    
    prompt = f"""
    {memory_context}
    
    Analyze this traveler:
    Name: {doc['name']}
    Permit: {doc['permit']}
    Backstory: {doc['backstory']}
    
    Provide a subtle hint about document authenticity without directly revealing if it's valid or not.
    Consider the border setting and recent history in your response.
    """
    
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
        str: Error description text
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

def ai_judge_document(doc, setting_context, memory_context, system_type="ai_judgment", max_tokens=300):
    """
    Use AI to judge if a document should be approved or denied.
    
    Args:
        doc (dict): The document to judge.
        setting_context (str): Context about the border setting.
        memory_context (str): Context about game history.
        
    Returns:
        dict: Judgment results including:
            - decision: "approve" or "deny"
            - confidence: float between 0-1
            - reasoning: explanation of the decision
            - suspicious_elements: list of suspicious elements if any
    """
    system_instruction = SYSTEM_INSTRUCTIONS.get(system_type, SYSTEM_INSTRUCTIONS["ai_judgment"])
    
    # Build a rich context for the AI to make an informed decision
    prompt = f"""
    {setting_context}
    
    {memory_context}
    
    DOCUMENT TO EVALUATE:
    Name: {doc['name']}
    Permit: {doc['permit']}
    Backstory: {doc['backstory']}
    
    Evaluate this document based on the border rules and situation.
    Determine if this traveler should be approved or denied entry.
    
    Format your response as JSON with the following fields:
    {{
      "decision": "approve" or "deny",
      "confidence": [value between 0-1],
      "reasoning": "Your detailed reasoning",
      "suspicious_elements": ["List any suspicious elements found", "or empty list if none"]
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.7,  # Lower temperature for more consistent judgments
                system_instruction=system_instruction
            )
        )
        
        # Parse the JSON response
        import json
        import re
        
        response_text = response.text
        
        # Try to extract a JSON object from the response text
        json_match = re.search(r'({.*})', response_text, re.DOTALL)
        if json_match:
            try:
                judgment = json.loads(json_match.group(1))
                # Ensure required fields are present
                required_fields = ["decision", "confidence", "reasoning", "suspicious_elements"]
                for field in required_fields:
                    if field not in judgment:
                        judgment[field] = "missing" if field != "confidence" else 0.5
                        
                return judgment
            except json.JSONDecodeError:
                logger.error("Failed to parse AI judgment as JSON")
        
        # Fallback if JSON parsing fails
        return {
            "decision": "approve" if random.random() > 0.3 else "deny",  # Default slightly biased toward approval
            "confidence": 0.5,
            "reasoning": "Unable to provide detailed reasoning due to parsing error.",
            "suspicious_elements": []
        }
            
    except Exception as e:
        logger.error(f"Error in AI judgment: {e}")
        # Fallback response
        return {
            "decision": "approve" if random.random() > 0.3 else "deny",
            "confidence": 0.5,
            "reasoning": "Error occurred during judgment.",
            "suspicious_elements": []
        }

def generate_narrative_update(current_state, decision, is_correct, memory_context=""):
    """
    Generate a narrative update based on player decisions.
    
    Args:
        current_state (dict): The current story state.
        decision (str): The player's decision (approve/deny).
        is_correct (bool): Whether the decision was correct.
        memory_context (str): Context from the memory manager.
        
    Returns:
        str: A narrative update.
    """
    corruption = current_state.get("corruption", 0)
    trust = current_state.get("trust", 0)
    
    prompt = f"""
    {memory_context}
    
    Player decision: {decision}
    Decision correctness: {'correct' if is_correct else 'incorrect'}
    Current corruption level: {corruption}
    Current trust level: {trust}
    
    Generate a brief narrative update (1-2 sentences) describing the consequences of this decision.
    Consider the border setting and game history in your response.
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
