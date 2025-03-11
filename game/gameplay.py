"""
Gameplay module for Veritaminal

Handles the core gameplay mechanics including document generation,
verification rules, and scoring.
"""

import random
import logging
from .api import generate_text, generate_document_error

logger = logging.getLogger(__name__)

class Rule:
    """
    Represents a verification rule for documents.
    """
    def __init__(self, name, description, check_function):
        """
        Initialize a rule.
        
        Args:
            name (str): Name of the rule.
            description (str): Description of the rule.
            check_function (callable): Function that checks if a document follows this rule.
        """
        self.name = name
        self.description = description
        self.check_function = check_function

    def check(self, document):
        """
        Check if a document follows this rule.
        
        Args:
            document (dict): The document to check.
            
        Returns:
            bool: True if the document follows this rule, False otherwise.
        """
        return self.check_function(document)


class GameplayManager:
    """
    Manages the gameplay mechanics.
    """
    def __init__(self):
        """
        Initialize the gameplay manager.
        """
        self.score = 0
        self.current_document = None
        self.rules = []
        self._initialize_rules()

    def _initialize_rules(self):
        """
        Initialize the basic verification rules.
        """
        # Rule 1: Permit must start with 'P'
        self.rules.append(
            Rule(
                "Permit Format",
                "All permits must start with the letter 'P'.",
                lambda doc: doc["permit"].startswith("P")
            )
        )
        
        # Rule 2: Permit must be followed by 4 digits
        self.rules.append(
            Rule(
                "Permit Number",
                "Permit numbers must have 4 digits after the 'P'.",
                lambda doc: len(doc["permit"]) == 5 and doc["permit"][1:].isdigit()
            )
        )
        
        # Rule 3: Name must have a first and last name
        self.rules.append(
            Rule(
                "Name Format",
                "Traveler names must include both first and last names.",
                lambda doc: len(doc["name"].split()) >= 2
            )
        )

    def add_rule(self, rule):
        """
        Add a new rule.
        
        Args:
            rule (Rule): The rule to add.
        """
        self.rules.append(rule)
        
    def generate_document(self):
        """
        Generate a new document.
        
        Returns:
            dict: The generated document.
        """
        name = generate_text("Generate a unique traveler name", "document_generation")
        permit = generate_text("Generate a permit number starting with 'P' followed by 4 digits", "document_generation")
        backstory = generate_text("Create a one-sentence backstory for a traveler", "document_generation")
        
        # Create the document
        document = {
            "name": name,
            "permit": permit,
            "backstory": backstory
        }
        
        # Decide if this document should have an error
        if random.random() < 0.3:  # 30% chance of error
            error_type, _ = generate_document_error()
            if error_type == "invalid_permit":
                # Introduce permit error
                if random.random() < 0.5:
                    document["permit"] = document["permit"].replace("P", "B")
                else:
                    document["permit"] += "X"
            elif error_type == "invalid_name":
                # Introduce name error (single name)
                name_parts = document["name"].split()
                if len(name_parts) > 1:
                    document["name"] = name_parts[0]
        
        # Check validity against rules
        document["is_valid"] = self.check_document_validity(document)
        
        self.current_document = document
        return document
    
    def check_document_validity(self, document):
        """
        Check if a document is valid according to all rules.
        
        Args:
            document (dict): The document to check.
            
        Returns:
            bool: True if the document is valid, False otherwise.
        """
        for rule in self.rules:
            if not rule.check(document):
                return False
        return True
    
    def make_decision(self, decision):
        """
        Make a decision on the current document.
        
        Args:
            decision (str): "approve" or "deny".
            
        Returns:
            tuple: (is_correct, points_earned)
        """
        if not self.current_document:
            logger.error("No current document to make a decision on.")
            return False, 0
        
        is_correct = (decision == "approve" and self.current_document["is_valid"]) or \
                     (decision == "deny" and not self.current_document["is_valid"])
        
        points = 1 if is_correct else 0
        self.score += points
        
        return is_correct, points
    
    def get_all_rules(self):
        """
        Get all current rules.
        
        Returns:
            list: List of all rules.
        """
        return self.rules
    
    def get_score(self):
        """
        Get the current score.
        
        Returns:
            int: The current score.
        """
        return self.score
