"""
Main menu module for Veritaminal

Handles the main menu system, game session management, and career progression.
"""

import os
import logging
import glob
from .gameplay import GameplayManager
from .settings import SettingsManager
from .ui import TerminalUI

logger = logging.getLogger(__name__)

class MainMenuManager:
    """
    Manages the main menu and game sessions.
    """
    def __init__(self):
        """
        Initialize the main menu manager.
        """
        self.ui = TerminalUI()
        self.gameplay_manager = GameplayManager()
        self.settings_manager = SettingsManager()
        self.career_stats = {
            "games_completed": 0,
            "total_score": 0,
            "borders_served": set(),
            "highest_day_reached": 0
        }
        
    def display_main_menu(self):
        """
        Display the main menu options.
        
        Returns:
            str: The selected option.
        """
        self.ui.clear_screen()
        print("\n" + "=" * self.ui.width)
        print("VERITAMINAL: Document Verification Game".center(self.ui.width))
        print("=" * self.ui.width + "\n")
        
        # Display career stats if any games have been played
        if self.career_stats["games_completed"] > 0:
            print("CAREER STATISTICS".center(self.ui.width))
            print(f"Games Completed: {self.career_stats['games_completed']}")
            print(f"Total Career Score: {self.career_stats['total_score']}")
            print(f"Borders Served: {len(self.career_stats['borders_served'])}")
            print(f"Highest Day Reached: {self.career_stats['highest_day_reached']}")
            print("\n" + "-" * self.ui.width + "\n")
        
        print("MAIN MENU".center(self.ui.width))
        options = [
            "1. Start New Career",
            "2. Continue Previous Career",
            "3. View Border Settings",
            "4. View Game Rules",
            "5. Quit Game"
        ]
        
        for option in options:
            print(option.center(self.ui.width))
            
        print("\n" + "=" * self.ui.width)
        
        choice = ""
        valid_choices = ["1", "2", "3", "4", "5"]
        while choice not in valid_choices:
            choice = input("\nEnter your selection (1-5): ")
            
        return choice
    
    def start_new_career(self):
        """
        Start a new game career with border selection.
        
        Returns:
            bool: True if a game was started, False otherwise.
        """
        # Display available border settings
        self.ui.clear_screen()
        print("\n" + "=" * self.ui.width)
        print("SELECT YOUR BORDER ASSIGNMENT".center(self.ui.width))
        print("=" * self.ui.width + "\n")
        
        settings = self.settings_manager.get_available_settings()
        for i, setting in enumerate(settings, 1):
            print(f"{i}. {setting['name']}")
            print(f"   {setting['description']}\n")
        
        # Let player choose a border or go back to main menu
        print("0. Return to Main Menu")
        
        choice = -1
        while choice < 0 or choice > len(settings):
            try:
                choice = int(input(f"\nEnter your choice (0-{len(settings)}): "))
            except ValueError:
                print("Please enter a valid number.")
                
        if choice == 0:
            return False  # Return to main menu
            
        # Initialize new game with selected border
        selected_setting = self.gameplay_manager.initialize_game(settings[choice-1]["id"])
        
        self.ui.clear_screen()
        print(f"\nYou selected: {selected_setting['name']}")
        print(f"\n{selected_setting['description']}\n")
        print("Current rules:")
        for rule in self.gameplay_manager.settings_manager.get_all_rules():
            print(f"- {rule}")
        
        input("\nPress Enter to begin your shift...")
        return True
    
    def continue_previous_career(self):
        """
        Load and continue a previous game career.
        
        Returns:
            bool: True if a game was loaded, False otherwise.
        """
        self.ui.clear_screen()
        print("\n" + "=" * self.ui.width)
        print("LOAD PREVIOUS CAREER".center(self.ui.width))
        print("=" * self.ui.width + "\n")
        
        # Get list of save files
        save_files = self._get_save_files()
        
        if not save_files:
            print("No saved games found.")
            input("\nPress Enter to return to main menu...")
            return False
        
        print("Available saved games:")
        for i, (save_path, save_name) in enumerate(save_files, 1):
            print(f"{i}. {save_name}")
        
        print("\n0. Return to Main Menu")
        
        choice = -1
        while choice < 0 or choice > len(save_files):
            try:
                choice = int(input(f"\nEnter your choice (0-{len(save_files)}): "))
            except ValueError:
                print("Please enter a valid number.")
                
        if choice == 0:
            return False  # Return to main menu
            
        # Load the selected save
        save_path, _ = save_files[choice-1]
        success = self.gameplay_manager.load_game(save_path)
        
        if success:
            print(f"\nGame loaded successfully!")
            
            # Display border info
            setting = self.gameplay_manager.settings_manager.get_current_setting()
            day = self.gameplay_manager.memory_manager.memory["game_state"]["day"]
            
            print(f"\nCurrent Assignment: {setting['name']}")
            print(f"Current Day: {day}")
            
            input("\nPress Enter to continue your shift...")
            return True
        else:
            print("\nFailed to load game.")
            input("\nPress Enter to return to main menu...")
            return False
    
    def view_border_settings(self):
        """
        Display information about all border settings.
        
        Returns:
            bool: Always False to return to main menu.
        """
        self.ui.clear_screen()
        print("\n" + "=" * self.ui.width)
        print("BORDER SETTINGS".center(self.ui.width))
        print("=" * self.ui.width + "\n")
        
        settings = self.settings_manager.get_available_settings()
        
        for setting in settings:
            print(f"= {setting['name']} =".center(self.ui.width))
            print(f"\n{setting['description']}")
            print(f"\nSituation: {setting['situation']}")
            
            print("\nDocument Requirements:")
            for req in setting['document_requirements']:
                print(f"- {req}")
                
            print("\nCommon Issues:")
            for issue in setting['common_issues']:
                print(f"- {issue}")
                
            print("\n" + "-" * self.ui.width + "\n")
        
        input("Press Enter to return to main menu...")
        return False
    
    def view_game_rules(self):
        """
        Display the core game rules.
        
        Returns:
            bool: Always False to return to main menu.
        """
        self.ui.clear_screen()
        print("\n" + "=" * self.ui.width)
        print("GAME RULES".center(self.ui.width))
        print("=" * self.ui.width + "\n")
        
        rules = [
            "As a border control agent, your job is to verify travel documents.",
            "Each traveler presents their document with a name, permit number, and backstory.",
            "Your task is to either APPROVE or DENY each traveler based on document validity.",
            "Valid permits must start with 'P' followed by exactly 4 digits.",
            "Traveler names must have both first and last names.",
            "Backstories should be consistent with the name.",
            "Additional requirements may be added based on your border assignment.",
            "Each day you will process multiple travelers.",
            "Making correct decisions improves your score.",
            "Careers last for 10 days, after which your performance is evaluated."
        ]
        
        for rule in rules:
            print(f"• {rule}")
        
        print("\n" + "-" * self.ui.width)
        print("\nCommands during gameplay:".center(self.ui.width))
        commands = [
            ("approve", "Approve the current traveler"),
            ("deny", "Deny the current traveler"),
            ("hint", "Request a hint from Veritas"),
            ("rules", "Display current verification rules"),
            ("save", "Save your current game progress"),
            ("help", "Show help information"),
            ("quit", "Return to main menu")
        ]
        
        for cmd, desc in commands:
            print(f"{cmd.ljust(10)} - {desc}")
            
        print("\n" + "=" * self.ui.width)
        input("\nPress Enter to return to main menu...")
        return False
    
    def update_career_stats(self, gameplay_manager):
        """
        Update career stats based on completed game.
        
        Args:
            gameplay_manager (GameplayManager): The gameplay manager with current game stats.
        """
        # Update career stats
        self.career_stats["games_completed"] += 1
        self.career_stats["total_score"] += gameplay_manager.score
        
        # Add border to borders served
        setting = gameplay_manager.settings_manager.get_current_setting()
        self.career_stats["borders_served"].add(setting["name"])
        
        # Update highest day reached
        day = gameplay_manager.memory_manager.memory["game_state"]["day"]
        self.career_stats["highest_day_reached"] = max(
            self.career_stats["highest_day_reached"],
            day
        )
    
    def _get_save_files(self):
        """
        Get list of available save files.
        
        Returns:
            list: List of (path, name) tuples for save files.
        """
        # Get the saves directory path
        saves_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            self.gameplay_manager.memory_manager.save_dir
        )
        
        # Get all JSON files in the saves directory
        save_pattern = os.path.join(saves_dir, "*.json")
        save_files = glob.glob(save_pattern)
        
        # Convert to (path, name) tuples
        return [(path, os.path.basename(path)) for path in save_files]