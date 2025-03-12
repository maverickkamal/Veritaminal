"""
Entry script to run the Veritaminal game.

This standalone script allows you to run the game without installing it as a package.
"""

import os
import sys
import argparse

# Add the project root directory to Python path to allow importing game modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function from the game package
from game.main import main

def parse_args():
    """Parse command-line arguments for the game launcher."""
    parser = argparse.ArgumentParser(
        description='Veritaminal: A Document Verification Game with Memory and Narrative',
        epilog='Example: python run_game.py --debug'
    )
    
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--load', type=str, help='Load a saved game from a specific file path')
    
    return parser.parse_args()

def print_welcome():
    """Print a welcome message with instructions."""
    print("\n" + "="*80)
    print(" VERITAMINAL: Enhanced Edition ".center(80, '='))
    print("="*80)
    print("\nWelcome to the enhanced version of Veritaminal!")
    print("This version includes:")
    print("- Border setting selection with tailored document rules")
    print("- AI judgment system that evaluates documents based on context")
    print("- Memory system that stores your decisions and creates a continuous story")
    print("- Save/load functionality to continue your career across sessions")
    print("\nStarting game...\n")

if __name__ == "__main__":
    # Display welcome message
    print_welcome()
    
    # Set up command line arguments to forward to the main game
    args = parse_args()
    
    # Convert args to list format for sys.argv
    sys_args = []
    if args.debug:
        sys_args.append('--debug')
    if args.load:
        sys_args.append('--load')
        sys_args.append(args.load)
    
    # Update sys.argv to pass arguments to main()
    sys.argv[1:] = sys_args
    
    # Run the game
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nGame interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        print("See veritaminal.log for details.")
        sys.exit(1)
