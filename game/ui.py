"""
UI module for Veritaminal

Handles the terminal-based user interface, including document display,
user input, and interface styling.
"""

import os
import sys
import logging
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import WordCompleter

logger = logging.getLogger(__name__)

# Define color styles
style = Style.from_dict({
    'title': '#ansiyellow bold',
    'header': '#ansiblue bold',
    'normal': '#ansiwhite',
    'error': '#ansired bold',
    'success': '#ansigreen',
    'warning': '#ansiyellow',
    'hint': '#ansicyan italic',
    'command': '#ansimagenta',
    'veritas': '#ansigreen bold',
})

# Command completer for auto-completion
command_completer = WordCompleter(['approve', 'deny', 'hint', 'rules', 'help', 'quit'])


class TerminalUI:
    """
    Manages the terminal-based user interface.
    """
    def __init__(self):
        """
        Initialize the terminal UI.
        """
        self.width = 80  # Default width
        self.adjust_terminal_size()
    
    def adjust_terminal_size(self):
        """
        Adjust UI based on terminal size.
        """
        try:
            # Get terminal size if available
            terminal_size = os.get_terminal_size()
            self.width = min(100, terminal_size.columns)
        except (AttributeError, OSError):
            # Default if terminal size can't be determined
            self.width = 80
    
    def clear_screen(self):
        """
        Clear the terminal screen.
        """
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_welcome(self):
        """
        Display the welcome message.
        """
        self.clear_screen()
        title = "VERITAMINAL: Document Verification Game"
        
        print("\n" + "=" * self.width)
        print(title.center(self.width))
        print("=" * self.width + "\n")
        
        welcome_text = [
            "Welcome to the border checkpoint.",
            "",
            "As a border control agent, your job is to verify travelers' documents",
            "and decide whether to approve or deny their entry.",
            "",
            "You'll be assisted by Veritas, an AI that may provide hints.",
            "",
            "Type 'help' for a list of commands.",
        ]
        
        for line in welcome_text:
            print(line.center(self.width))
        
        print("\n" + "=" * self.width + "\n")
        
        input("Press Enter to begin your shift...".center(self.width))
    
    def display_document(self, document):
        """
        Display a document to the player.
        
        Args:
            document (dict): The document to display.
        """
        self.clear_screen()
        print("\n" + "-" * self.width)
        print("TRAVELER DOCUMENT".center(self.width))
        print("-" * self.width + "\n")
        
        # Display document details with formatting
        print(f"Name:      {document['name']}")
        print(f"Permit:    {document['permit']}")
        print(f"\nBackstory: {document['backstory']}")
        
        print("\n" + "-" * self.width)
    
    def display_veritas_hint(self, hint):
        """
        Display a hint from Veritas.
        
        Args:
            hint (str): The hint to display.
        """
        print("\n" + "-" * self.width)
        print("VERITAS SAYS:".center(self.width))
        print(f"\n\"{hint}\"\n")
        print("-" * self.width)
    
    def display_rules(self, rules):
        """
        Display the current verification rules.
        
        Args:
            rules (list): List of Rule objects.
        """
        self.clear_screen()
        print("\n" + "-" * self.width)
        print("VERIFICATION RULES".center(self.width))
        print("-" * self.width + "\n")
        
        for i, rule in enumerate(rules, 1):
            print(f"{i}. {rule.name}: {rule.description}")
        
        print("\n" + "-" * self.width)
        input("\nPress Enter to return...")
    
    def display_help(self):
        """
        Display help information.
        """
        self.clear_screen()
        print("\n" + "-" * self.width)
        print("AVAILABLE COMMANDS".center(self.width))
        print("-" * self.width + "\n")
        
        commands = [
            ("approve", "Approve the current traveler"),
            ("deny", "Deny the current traveler"),
            ("hint", "Request a hint from Veritas"),
            ("rules", "Display current verification rules"),
            ("help", "Show this help information"),
            ("quit", "Exit the game")
        ]
        
        for cmd, desc in commands:
            print(f"{cmd.ljust(10)} - {desc}")
        
        print("\n" + "-" * self.width)
        input("\nPress Enter to return...")
    
    def display_feedback(self, is_correct, narrative_update):
        """
        Display feedback based on the player's decision.
        
        Args:
            is_correct (bool): Whether the player's decision was correct.
            narrative_update (str): The narrative update to display.
        """
        if is_correct:
            print("\n✓ Correct decision!")
        else:
            print("\n✗ Incorrect decision!")
        
        print(f"\n{narrative_update}")
    
    def display_game_over(self, ending_type, ending_message):
        """
        Display the game over screen.
        
        Args:
            ending_type (str): Type of ending ('good', 'bad', 'corrupt', 'strict').
            ending_message (str): The ending message to display.
        """
        self.clear_screen()
        print("\n" + "=" * self.width)
        print("GAME OVER".center(self.width))
        print("=" * self.width + "\n")
        
        print(ending_message.center(self.width) + "\n")
        
        if ending_type == 'good':
            print("Congratulations! You've successfully completed your mission.".center(self.width))
        
        print("\n" + "=" * self.width)
        input("\nPress Enter to exit...".center(self.width))
    
    def get_user_input(self):
        """
        Get input from the user with command completion.
        
        Returns:
            str: The user's command.
        """
        try:
            user_input = prompt(
                'Enter command > ',
                completer=command_completer,
                style=style
            )
            return user_input.strip().lower()
        except KeyboardInterrupt:
            return "quit"
    
    def display_status(self, day, score, state_summary):
        """
        Display status information.
        
        Args:
            day (int): Current day.
            score (int): Current score.
            state_summary (str): Summary of the narrative state.
        """
        print("\n" + "-" * self.width)
        print(f"Day: {day} | Score: {score}")
        print(state_summary)
        print("-" * self.width)
