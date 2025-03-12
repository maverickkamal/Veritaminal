"""
Main module for Veritaminal

Entry point for the game that initializes components and runs the main game loop.
"""

import sys
import logging
import argparse
import os
from .api import get_veritas_hint, generate_narrative_update
from .gameplay import GameplayManager, Rule  # Added Rule import here
from .narrative import NarrativeManager
from .ui import TerminalUI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='veritaminal.log'
)

logger = logging.getLogger(__name__)

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Veritaminal: Terminal-Based Document Verification Game')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--load', type=str, help='Load a saved game file')
    return parser.parse_args()

def main():
    """
    Main entry point for the game.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Configure logging level based on args
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize components
    logger.info("Starting Veritaminal game")
    try:
        # Initialize game components
        ui = TerminalUI()
        gameplay_manager = GameplayManager()
        narrative_manager = NarrativeManager()
        
        # Display welcome screen
        ui.display_welcome()
        
        # Load game or start a new one
        if args.load and os.path.exists(args.load):
            if gameplay_manager.load_game(args.load):
                print(f"\nGame loaded successfully from {args.load}")
                
                # Synchronize narrative manager with memory manager's state
                narrative_manager.story_state["day"] = gameplay_manager.memory_manager.memory["game_state"]["day"]
                narrative_manager.story_state["corruption"] = gameplay_manager.memory_manager.memory["game_state"]["corruption"]
                narrative_manager.story_state["trust"] = gameplay_manager.memory_manager.memory["game_state"]["trust"]
            else:
                print(f"\nFailed to load game from {args.load}")
                return 1
        else:
            # Select border setting for a new game
            settings = gameplay_manager.settings_manager.get_available_settings()
            print("\nSelect a border setting:")
            for i, setting in enumerate(settings, 1):
                print(f"{i}. {setting['name']} - {setting['description']}")
            
            choice = 0
            while choice < 1 or choice > len(settings):
                try:
                    choice = int(input(f"\nEnter selection (1-{len(settings)}): "))
                except ValueError:
                    print("Please enter a number.")
            
            selected_setting = gameplay_manager.initialize_game(settings[choice-1]["id"])
            print(f"\nYou selected: {selected_setting['name']}")
            print(f"\n{selected_setting['description']}\n")
            print("Current rules:")
            for rule in gameplay_manager.settings_manager.get_all_rules():
                print(f"- {rule}")
            
            input("\nPress Enter to begin your shift...")
        
        # Main game loop
        game_running = True
        while game_running:
            # Check if game is over
            is_game_over, ending_type, ending_message = narrative_manager.check_game_over()
            if is_game_over:
                ui.display_game_over(ending_type, ending_message)
                # Reset memory on game over
                gameplay_manager.memory_manager.reset_memory()
                break
            
            # Generate new document for current day
            document = gameplay_manager.generate_document()
            ui.display_document(document)
            
            # Display status
            ui.display_status(
                narrative_manager.story_state["day"],
                gameplay_manager.get_score(),
                narrative_manager.get_state_summary()
            )
            
            # Process commands until player makes a decision (approve/deny)
            decision_made = False
            while not decision_made and game_running:
                command = ui.get_user_input()
                
                if command == "approve" or command == "deny":
                    # Process decision
                    is_correct, points = gameplay_manager.make_decision(command)
                    
                    # Generate narrative update with memory context
                    memory_context = gameplay_manager.memory_manager.get_memory_context()
                    narrative_update = generate_narrative_update(
                        narrative_manager.story_state,
                        command,
                        is_correct,
                        memory_context
                    )
                    
                    # Update narrative state
                    narrative_manager.update_state(command, is_correct, document)
                    
                    # Sync narrative manager with gameplay manager's memory
                    narrative_manager.story_state["corruption"] = gameplay_manager.memory_manager.memory["game_state"]["corruption"]
                    narrative_manager.story_state["trust"] = gameplay_manager.memory_manager.memory["game_state"]["trust"]
                    
                    # Display feedback and AI reasoning if available
                    ui.display_feedback(is_correct, narrative_update)
                    if command != gameplay_manager.ai_judgment["decision"]:
                        print("\nAI Opinion:")
                        print(f"The AI would have {gameplay_manager.ai_judgment['decision']}ed because: {gameplay_manager.get_ai_reasoning()}")
                    
                    decision_made = True
                    
                    # Save game after each decision
                    gameplay_manager.save_game()
                    
                    # Wait for player to continue
                    input("\nPress Enter to continue...")
                    
                elif command == "hint":
                    # Get and display hint with memory context
                    memory_context = gameplay_manager.memory_manager.get_memory_context()
                    hint = get_veritas_hint(document, memory_context)
                    ui.display_veritas_hint(hint)
                    
                elif command == "rules":
                    # Display rules from the current setting
                    setting_rules = gameplay_manager.settings_manager.get_all_rules()
                    ui.display_rules([Rule(f"Rule {i+1}", rule, lambda doc: True) 
                                     for i, rule in enumerate(setting_rules)])
                    ui.display_document(document)  # Re-display document after rules
                    
                elif command == "help":
                    # Display help
                    ui.display_help()
                    ui.display_document(document)  # Re-display document after help
                    
                elif command == "save":
                    # Save game
                    if gameplay_manager.save_game():
                        print("\nGame saved successfully.")
                    else:
                        print("\nFailed to save game.")
                        
                elif command == "quit":
                    # Quit game
                    game_running = False
                    print("\nThank you for playing Veritaminal!")
                    
                else:
                    # Invalid command
                    print("\nInvalid command. Type 'help' for a list of commands.")
            
            # Advance to next day if a decision was made
            if decision_made:
                day_message = narrative_manager.advance_day()
                
                # Sync day between narrative and memory managers
                gameplay_manager.memory_manager.memory["game_state"]["day"] = narrative_manager.story_state["day"]
                
                print(f"\n{day_message}")
                input("\nPress Enter to continue...")
                
        return 0
    
    except KeyboardInterrupt:
        logger.info("Game interrupted by user")
        print("\nGame interrupted. Goodbye!")
        return 0
    
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\nAn unexpected error occurred: {e}")
        print("See veritaminal.log for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
