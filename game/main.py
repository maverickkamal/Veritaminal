"""
Main module for Veritaminal

Entry point for the game that initializes components and runs the main game loop.
"""

import sys
import logging
import argparse
from .api import get_veritas_hint
from .gameplay import GameplayManager
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
        
        # Main game loop
        game_running = True
        while game_running:
            # Check if game is over
            is_game_over, ending_type, ending_message = narrative_manager.check_game_over()
            if is_game_over:
                ui.display_game_over(ending_type, ending_message)
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
                    narrative_update = narrative_manager.update_state(command, is_correct, document)
                    ui.display_feedback(is_correct, narrative_update)
                    decision_made = True
                    
                    # Wait for player to continue
                    input("\nPress Enter to continue...")
                    
                elif command == "hint":
                    # Get and display hint
                    hint = get_veritas_hint(document)
                    ui.display_veritas_hint(hint)
                    
                elif command == "rules":
                    # Display rules
                    ui.display_rules(gameplay_manager.get_all_rules())
                    ui.display_document(document)  # Re-display document after rules
                    
                elif command == "help":
                    # Display help
                    ui.display_help()
                    ui.display_document(document)  # Re-display document after help
                    
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
