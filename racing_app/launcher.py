"""
Racing Game Controller - Unified Launcher
Single entry point: Overlay always runs + Menu to select game mode

@nandurstudio
Date Created: 2025-12-01
Last Modified: 2026-02-03
"""

import asyncio
import sys
import os
import json
import subprocess
import time
import logging

# Force UTF-8 output on Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def save_config(config: dict, filename: str = "config.json"):
    """Save configuration to JSON file"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, filename)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"[WARNING] Failed to save config: {e}")
        return False


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("RACING GAME CONTROLLER - LAUNCHER")
    print("="*70 + "\n")


def get_mode_choice(config: dict):
    """Ask user: Real TikTok or Mock? (Overlay always runs)"""
    print("SELECT MODE")
    print("-" * 70)
    print("1. REAL TikTok       - Connect to actual TikTok LIVE stream")
    print("2. MOCK              - Test with simulated viewers (no internet)")
    print("3. EXIT              - Close the launcher & overlay")
    print()
    
    last_mode = config.get("last_session", {}).get("mode")
    if last_mode and last_mode != "overlay":
        last_mode_num = {"real": "1", "mock": "2"}.get(last_mode, "1")
        print(f"[LAST] {last_mode_num}. {last_mode.upper()}")
        print()
    
    while True:
        choice = input("Choose mode (1, 2, or 3): ").strip()
        if choice in ['1', '2', '3']:
            mode_map = {'1': 'real', '2': 'mock', '3': 'exit'}
            selected = mode_map[choice]
            # Save last session
            if "last_session" not in config:
                config["last_session"] = {}
            if selected != 'exit':
                config["last_session"]["mode"] = selected
            return selected
        print("[ERROR] Invalid choice. Please enter 1, 2, or 3")


def get_debug_choice(config: dict):
    """Ask user: Debug or Production?"""
    print("\nSELECT DEBUG MODE")
    print("-" * 70)
    print("1. DEBUG Mode        - Safe testing (NO actual keyboard input)")
    print("2. PRODUCTION Mode   - Real keyboard input to game")
    print()
    
    last_debug = config.get("last_session", {}).get("debug_mode", False)
    last_debug_num = "1" if last_debug else "2"
    debug_text = "DEBUG (Safe)" if last_debug else "PRODUCTION (Real)"
    print(f"[LAST] {last_debug_num}. {debug_text}")
    print()
    
    while True:
        choice = input("Choose debug mode (1 or 2): ").strip()
        if choice in ['1', '2']:
            debug_mode = choice == '1'
            # Save last session
            if "last_session" not in config:
                config["last_session"] = {}
            config["last_session"]["debug_mode"] = debug_mode
            return debug_mode
        print("[ERROR] Invalid choice. Please enter 1 or 2")


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
    last_game = config.get("last_session", {}).get("game", active_game)
    
    if not games:
        print("[ERROR] No games configured in config.json")
        return None
    
    for i, game in enumerate(games, 1):
        marker = " [LAST PLAYED]" if game == last_game else ""
        print(f"{i}. {game}{marker}")
    
    print()
    
    while True:
        try:
            choice = input(f"Choose game (1-{len(games)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(games):
                selected = games[idx]
                # Save last session
                if "last_session" not in config:
                    config["last_session"] = {}
                config["last_session"]["game"] = selected
                return selected
        except ValueError:
            pass
        
        print(f"[ERROR] Invalid choice. Please enter 1-{len(games)}")


def run_overlay_background():
    """Start overlay as background process (non-blocking)"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        overlay_file = os.path.join(script_dir, "live_overlay_electron.py")
        
        # Kill any existing overlay processes first
        print("[INFO] 🔍 Checking for existing overlay...")
        try:
            import psutil
            for proc in psutil.process_iter(['name', 'cmdline']):
                try:
                    # Check if it's electron process running our overlay
                    if proc.info['name'] and 'electron' in proc.info['name'].lower():
                        cmdline = proc.info.get('cmdline', [])
                        if cmdline and any('live-instruction-electron.html' in str(arg) for arg in cmdline):
                            print(f"[INFO] 🛑 Killing existing overlay (PID: {proc.pid})...")
                            proc.kill()
                            proc.wait(timeout=3)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            print(f"[WARNING] Could not check for existing overlay: {e}")
        
        print("[INFO] 🎮 Starting live instruction overlay (Electron)...")
        
        # Start as background process (non-blocking)
        # Use PIPE instead of DEVNULL to prevent handle issues on Windows
        # Suppress output without keeping invalid handles
        try:
            process = subprocess.Popen(
                [sys.executable, overlay_file],
                cwd=script_dir,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            )
        except Exception as e:
            print(f"[ERROR] Failed to create process: {e}")
            return None
        
        print("[SUCCESS] ✅ Overlay started (background)\n")
        return process
        
    except Exception as e:
        print(f"[ERROR] Failed to start overlay: {e}")
        return None


def run_real_mode(debug_mode, config_data=None, game_name=None):
    """Run real TikTok mode"""
    print("\n" + "="*70)
    print("REAL TIKTOK MODE")
    print("="*70 + "\n")
    
    sys.path.insert(0, 'examples')
    from racing_game_controller import pre_checklist, RacingGameController
    
    try:
        # Load config if not provided
        if not config_data:
            config_data = load_config("config.json")
            if not config_data:
                print("[ERROR] config.json not found!")
                return
        
        # Get game if not provided
        if not game_name:
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
        
        # Get custom mappings for animations
        custom_mappings = game_config.get("custom_mappings", {})
        
        # Create controller with game name and custom mappings
        controller = RacingGameController(
            unique_id=username,
            debug_mode=debug_mode,
            game_name=game_name,
            custom_mappings=custom_mappings
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
        print(f"Press Ctrl+C to stop")
        print("="*70)
        print("LIVE CONSOLE OUTPUT")
        print("="*70 + "\n")
        controller.run_blocking()
        
    except KeyboardInterrupt:
        print("\n\n[CLOSED] Thanks for playing!")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

def run_mock_mode(debug_mode, config_data=None, game_name=None):
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
    
    # Load config if not provided
    if not config_data:
        config_data = load_config("config.json")
        if not config_data:
            print("[ERROR] config.json not found!")
            return
    
    # Get game if not provided
    if not game_name:
        game_name = get_game_choice(config_data)
        if not game_name:
            print("[ERROR] No game selected!")
            return
    
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
    
    # Get game-specific config
    game_config = config_data["games"].get(game_name, {})
    
    # Create controller with game name
    controller = RacingGameController('@mock_user', debug_mode=debug_mode, game_name=game_name)
    
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
    """Main launcher entry point"""
    print_banner()
    
    # Load config
    config = load_config()
    if config is None:
        config = {}
    
    overlay_process = None
    
    try:
        # STEP 1: Always start overlay first (background)
        print("="*70)
        print("STARTING OVERLAY")
        print("="*70)
        overlay_process = run_overlay_background()
        
        time.sleep(1)  # Give overlay 1 second to start
        
        # STEP 2: Show menu loop
        print("="*70)
        print("MAIN MENU - Overlay is running in background")
        print("="*70 + "\n")
        
        while True:
            # Get user choice
            mode = get_mode_choice(config)
            
            # Exit option
            if mode == 'exit':
                print("\n" + "="*70)
                print("SHUTTING DOWN")
                print("="*70)
                print("[INFO] Closing overlay...")
                if overlay_process:
                    try:
                        # Kill entire process tree (including Electron and Node)
                        import psutil
                        parent = psutil.Process(overlay_process.pid)
                        children = parent.children(recursive=True)
                        
                        # Kill all children first
                        for child in children:
                            try:
                                print(f"[INFO] Killing child process {child.pid} ({child.name()})...")
                                child.kill()
                            except:
                                pass
                        
                        # Kill parent
                        print(f"[INFO] Killing parent process {parent.pid}...")
                        parent.kill()
                        
                        # Wait for all to finish
                        psutil.wait_procs(children + [parent], timeout=3)
                        print("[SUCCESS] Overlay closed successfully")
                    except Exception as ex:
                        print(f"[WARNING] Normal kill failed: {ex}")
                        try:
                            # Fallback: taskkill for Windows
                            if sys.platform == 'win32':
                                print("[INFO] Using taskkill as fallback...")
                                subprocess.run(['taskkill', '/F', '/T', '/PID', str(overlay_process.pid)], 
                                             capture_output=True, timeout=5)
                        except:
                            pass
                    finally:
                        # Properly close the Popen handle to avoid OSError in __del__
                        try:
                            overlay_process.terminate()
                        except:
                            pass
                        try:
                            overlay_process.wait(timeout=1)
                        except:
                            pass
                        # Close file descriptors
                        try:
                            if overlay_process.stdout:
                                overlay_process.stdout.close()
                            if overlay_process.stderr:
                                overlay_process.stderr.close()
                            if overlay_process.stdin:
                                overlay_process.stdin.close()
                        except:
                            pass
                print("[INFO] ✅ Goodbye!")
                return
            
            # Get debug choice
            debug = get_debug_choice(config)
            game_name = get_game_choice(config)
            
            # Show summary
            mode_text = "REAL TikTok" if mode == 'real' else "MOCK Testing"
            debug_text = "DEBUG (Safe)" if debug else "PRODUCTION (Real)"
            
            print("\n" + "="*70)
            print("CONFIGURATION SUMMARY")
            print("="*70)
            print(f"Mode:        {mode_text}")
            print(f"Debug:       {debug_text}")
            print(f"Game:        {game_name}")
            print("Overlay:     Running ✅")
            print("="*70 + "\n")
            
            input("Press Enter to continue...")
            
            # Save config before running
            save_config(config)
            
            # Run selected mode
            try:
                if mode == 'real':
                    run_real_mode(debug, config, game_name)
                else:
                    run_mock_mode(debug, config, game_name)
                
                # After game ends, show menu again
                print("\n" + "="*70)
                print("Game ended. Returning to menu...")
                print("="*70 + "\n")
                input("Press Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n[INFO] Game interrupted. Returning to menu...\n")
                input("Press Enter to continue...")
            except Exception as e:
                print(f"\n❌ Game error: {e}")
                import traceback
                traceback.print_exc()
                input("\nPress Enter to continue...")
    
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("LAUNCHER INTERRUPTED")
        print("="*70)
        if overlay_process:
            try:
                # Kill entire process tree
                import psutil
                parent = psutil.Process(overlay_process.pid)
                children = parent.children(recursive=True)
                
                for child in children:
                    try:
                        child.kill()
                    except:
                        pass
                
                parent.kill()
                psutil.wait_procs(children + [parent], timeout=3)
            except Exception as ex:
                try:
                    if sys.platform == 'win32':
                        subprocess.run(['taskkill', '/F', '/T', '/PID', str(overlay_process.pid)], 
                                     capture_output=True, timeout=5)
                except:
                    pass
        print("[INFO] ✅ Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        if overlay_process:
            try:
                # Kill entire process tree
                import psutil
                parent = psutil.Process(overlay_process.pid)
                children = parent.children(recursive=True)
                
                for child in children:
                    try:
                        child.kill()
                    except:
                        pass
                
                parent.kill()
                psutil.wait_procs(children + [parent], timeout=3)
            except Exception as ex:
                try:
                    if sys.platform == 'win32':
                        subprocess.run(['taskkill', '/F', '/T', '/PID', str(overlay_process.pid)], 
                                     capture_output=True, timeout=5)
                except:
                    pass


if __name__ == "__main__":
    main()
