"""
Racing Game Controller - Unified Launcher
Single entry point for all modes: Real/Mock x Debug/Production
"""

import asyncio
import sys
import os
import json

# Force UTF-8 output on Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("RACING GAME CONTROLLER - LAUNCHER")
    print("="*70 + "\n")


def get_mode_choice():
    """Ask user: Real TikTok or Mock?"""
    print("SELECT MODE")
    print("-" * 70)
    print("1. REAL TikTok       - Connect to actual TikTok LIVE stream")
    print("2. MOCK              - Test with simulated viewers (no internet)")
    print()
    
    while True:
        choice = input("Choose mode (1 or 2): ").strip()
        if choice in ['1', '2']:
            return 'real' if choice == '1' else 'mock'
        print("[ERROR] Invalid choice. Please enter 1 or 2")


def get_debug_choice():
    """Ask user: Debug or Production?"""
    print("\nSELECT DEBUG MODE")
    print("-" * 70)
    print("Debug Mode       - Safe testing (NO actual keyboard input)")
    print("Production Mode  - Real keyboard input to game")
    print()
    
    while True:
        choice = input("Use DEBUG mode? (yes/no): ").strip().lower()
        if choice in ['yes', 'y', '1']:
            return True
        elif choice in ['no', 'n', '0']:
            return False
        print("[ERROR] Invalid choice. Please enter yes or no")


def load_config(filename: str = "config.json") -> dict | None:
    """Load configuration from JSON file"""
    try:
        # Get the directory where launcher.py is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, filename)
        
        if not os.path.exists(config_path):
            return None
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return config
    except Exception as e:
        print(f"[ERROR] Failed to load config: {e}")
        return None


def get_game_choice(config: dict):
    """Ask user to select game"""
    print("\nSELECT GAME")
    print("-" * 70)
    
    games = list(config.get("games", {}).keys())
    active_game = config.get("active_game", games[0] if games else None)
    
    if not games:
        print("[ERROR] No games configured in config.json")
        return None
    
    for i, game in enumerate(games, 1):
        marker = " [CURRENT]" if game == active_game else ""
        print(f"{i}. {game}{marker}")
    
    print()
    
    while True:
        try:
            choice = input(f"Choose game (1-{len(games)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(games):
                return games[idx]
        except ValueError:
            pass
        
        print(f"[ERROR] Invalid choice. Please enter 1-{len(games)}")


def run_real_mode(debug_mode):
    """Run real TikTok mode"""
    print("\n" + "="*70)
    print("REAL TIKTOK MODE")
    print("="*70 + "\n")
    
    sys.path.insert(0, 'examples')
    from racing_game_controller import pre_checklist, RacingGameController
    
    try:
        # Load config
        config_data = load_config("config.json")
        if not config_data:
            print("[ERROR] config.json not found!")
            return
        
        # Select game
        game_name = get_game_choice(config_data)
        if not game_name:
            print("[ERROR] No game selected!")
            return
        
        # Get game-specific config
        game_config = config_data["games"].get(game_name, {})
        username = config_data.get("username", "")
        
        print(f"\n[LOADED] Game: {game_name}")
        print(f"[LOADED] User: @{username}")
        
        # Pre-flight checklist (verify username and stream)
        username = asyncio.run(pre_checklist())
        if username is None:
            print("Setup cancelled by user")
            return
        
        # Create controller with game name
        controller = RacingGameController(
            unique_id=username,
            debug_mode=debug_mode,
            game_name=game_name
        )
        
        # Apply game-specific settings
        if game_config.get("cooldown"):
            controller.set_cooldown(per_user_duration=game_config.get("cooldown"))
        
        if game_config.get("hold_duration"):
            controller.set_hold_duration(game_config.get("hold_duration"))
        
        if game_config.get("custom_mappings"):
            print("[ADDING] Custom mappings for", game_name)
            for command, key in game_config.get("custom_mappings", {}).items():
                controller.add_mapping(command, key)
        
        print(f"\n[STARTING] Racing Game Controller for {game_name}...")
        print(f"Press Ctrl+C to stop\n")
        controller.run_blocking()
        
    except KeyboardInterrupt:
        print("\n\n[CLOSED] Thanks for playing!")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

def run_mock_mode(debug_mode):
    """Run mock testing mode"""
    print("\n" + "="*70)
    print("MOCK MODE - Testing with Simulated Viewers")
    print("="*70 + "\n")
    
    sys.path.insert(0, 'examples')
    
    # Import mock test components
    import logging
    from racing_game_controller import RacingGameController
    from pynput.keyboard import Controller
    
    logger = logging.getLogger(__name__)
    
    # Configure logging for mock
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('racing_controller.log'),
            logging.StreamHandler()
        ]
    )
    
    # Setup mock data
    class MockUser:
        def __init__(self, unique_id, nickname):
            self.unique_id = unique_id
            self.nickname = nickname
    
    class MockCommentEvent:
        def __init__(self, username, comment):
            self.user = MockUser(f"user_{username}", username)
            self.comment = comment
    
    # Create controller
    controller = RacingGameController('@mock_user', debug_mode=debug_mode)
    
    # Simulate viewers
    mock_viewers = [
        ("Adi", "w"),
        ("Budi", "maju"),
        ("Citra", "a"),
        ("Dedi", "kanan"),
        ("Eka", "jump"),
        ("Fajar", "lompat"),
        ("Gina", "unknown_command"),
        ("Hendra", "s"),
        ("Ira", "w"),
        ("Joko", "w"),
    ]
    
    print(f"[MOCK LIVE STARTED]\n")
    print(f"Simulating {len(mock_viewers)} viewers...\n")
    
    import time
    from datetime import datetime
    
    for idx, (username, command) in enumerate(mock_viewers, 1):
        print(f"Message {idx}/{len(mock_viewers)}")
        print(f"Incoming: [{username}]: {command}")
        
        # Simulate event handler
        mock_event = MockCommentEvent(username, command)
        
        # Manually call handler logic (simpler than async)
        command_lower = command.lower().strip()
        key = controller.key_mapping.get(command_lower)
        if key:
            print(f"[KEY PRESS] {key} (0.1s)")
            controller._update_stats(command_lower, mock_event.user.unique_id, username)
        
        time.sleep(0.5)
    
    print(f"\n[MOCK LIVE ENDED]\n")
    controller._print_stats()
    print("[SUCCESS] Mock testing completed successfully!")


def main():
    """Main launcher"""
    print_banner()
    
    # Get user choices
    mode = get_mode_choice()
    debug = get_debug_choice()
    
    # Show summary
    mode_text = "REAL TikTok" if mode == 'real' else "MOCK Testing"
    debug_text = "DEBUG (Safe)" if debug else "PRODUCTION (Real)"
    
    print("\n" + "="*70)
    print("CONFIGURATION SUMMARY")
    print("="*70)
    print(f"Mode:        {mode_text}")
    print(f"Debug:       {debug_text}")
    print("="*70 + "\n")
    
    input("Press Enter to continue...")
    
    # Run selected mode
    try:
        if mode == 'real':
            run_real_mode(debug)
        else:
            run_mock_mode(debug)
    except KeyboardInterrupt:
        print("\n\n👋 Launcher closed")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
