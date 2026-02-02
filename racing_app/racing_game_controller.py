"""
TikTok Live Racing Game Controller
Real-time WASD control from TikTok live chat

Supports racing games like:
- Minecraft Racing
- GTA
- Roblox Racing
- Need for Speed
- Any game with WASD controls
"""

import asyncio
import logging
import sys
import io
import json
import os
from pynput.keyboard import Controller, Key
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent, DisconnectEvent
from typing import Dict, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configure logging with UTF-8 support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('racing_controller.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class UserCooldown:
    """Track per-user cooldown"""
    last_command_time: datetime = field(default_factory=datetime.now)
    cooldown_duration: float = 0.1
    
    def is_on_cooldown(self) -> bool:
        """Check if user is on cooldown"""
        elapsed = (datetime.now() - self.last_command_time).total_seconds()
        return elapsed < self.cooldown_duration
    
    def reset(self):
        """Reset cooldown timer"""
        self.last_command_time = datetime.now()


class RacingGameController:
    """
    Racing Game Controller
    Maps TikTok chat commands to WASD keyboard input
    """
    
    def __init__(self, unique_id: str, debug_mode: bool = True, game_name: str = "Game"):
        """
        Initialize racing game controller
        
        Args:
            unique_id: TikTok username (without @)
            debug_mode: True = no keyboard input, False = real keyboard
            game_name: Name of the game being played (for logging)
        """
        self.unique_id = unique_id
        self.debug_mode = debug_mode
        self.game_name = game_name
        
        # TikTok client
        self.client = TikTokLiveClient(unique_id=unique_id)
        
        # Keyboard controller
        self.keyboard = Controller()
        
        # Key mapping for racing games
        self.key_mapping = {
            # Forward/Gas
            "w": "w",
            "forward": "w",
            "maju": "w",
            "gas": "w",
            "accelerate": "w",
            
            # Backward/Brake
            "s": "s",
            "backward": "s",
            "mundur": "s",
            "brake": "s",
            "reverse": "s",
            
            # Left
            "a": "a",
            "left": "a",
            "kiri": "a",
            "turn_left": "a",
            
            # Right
            "d": "d",
            "right": "d",
            "kanan": "d",
            "turn_right": "d",
            
            # Drift/Handbrake
            "drift": "space",
            "handbrake": "space",
            "drift_left": "q",
            "drift_right": "e",
            
            # Special (game-specific)
            "nitro": "shift",
            "boost": "shift",
            "turbo": "shift",
            "jump": "space",
            "lompat": "space",
        }
        
        # Combination keys (multiple keys held together)
        self.combination_keys = {
            "ws": ["w", "s"],     # Forward + Backward (drifting)
            "wd": ["w", "d"],     # Forward + Right turn
            "as": ["a", "s"],     # Left + Backward (backward left)
            "sd": ["s", "d"],     # Backward + Right (backward right)
        }
        
        # User cooldowns (prevent spam)
        self.user_cooldowns: Dict[str, UserCooldown] = {}
        self.global_cooldown_duration = 0.05  # Global cooldown in seconds
        self.per_user_cooldown_duration = 0.2  # Per-user cooldown in seconds
        
        # Statistics
        self.stats = {
            "total_commands": 0,
            "total_users": 0,
            "unique_users": set(),
            "commands_by_type": {},
            "start_time": datetime.now(),
        }
        
        # Pressed keys tracking (for continuous press)
        self.currently_pressed = set()
        self.press_duration = 0.1  # How long to hold key (default)
        self.movement_hold_duration = 5.0  # Hold duration for W/A/S/D (seconds)
        
        # Movement keys that should be held
        self.movement_keys = {"w", "a", "s", "d"}
        
        # Register event handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all event handlers"""
        
        @self.client.on(ConnectEvent)
        async def on_connect(event: ConnectEvent):
            logger.info(f"[CONNECTED] @{event.unique_id} (Room ID: {self.client.room_id})")
            logger.info(f"Game: {self.game_name} | Racing Game Controller {'[DEBUG MODE - NO KEYBOARD]' if self.debug_mode else '[PRODUCTION MODE]'}")
        
        @self.client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            await self._handle_comment(event)
        
        @self.client.on(DisconnectEvent)
        async def on_disconnect(event: DisconnectEvent):
            logger.warning("[DISCONNECTED] from stream")
            self._print_stats()
    
    async def _handle_comment(self, event: CommentEvent):
        """Handle incoming comment"""
        command = event.comment.lower().strip()
        user_id = event.user.unique_id
        username = event.user.nickname
        
        # Get or create user cooldown
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = UserCooldown(
                cooldown_duration=self.per_user_cooldown_duration
            )
        
        user_cooldown = self.user_cooldowns[user_id]
        
        # Check if this is a combination key command
        combination = self.combination_keys.get(command)
        if combination:
            # Check per-user cooldown
            if user_cooldown.is_on_cooldown():
                return  # Ignore if too fast
            
            # Hold multiple keys
            await self._hold_multiple_keys(combination, self.movement_hold_duration)
            user_cooldown.reset()
            
            # Update statistics
            self._update_stats(command, user_id, username)
            
            keys_text = " + ".join([k.upper() for k in combination])
            logger.info(f"{username:20} -> '{command:15}' => {keys_text} (held {self.movement_hold_duration}s)")
            return
        
        # Check if command is mapped
        key = self.key_mapping.get(command)
        if not key:
            return  # Ignore unmapped commands
        
        # Check per-user cooldown
        if user_cooldown.is_on_cooldown():
            return  # Ignore if too fast
        
        # Check if this is a movement key that should be held
        if key in self.movement_keys:
            # Hold movement keys for 5 seconds
            await self._hold_key(key, self.movement_hold_duration)
        else:
            # Press other keys briefly
            await self._press_key(key)
        
        user_cooldown.reset()
        
        # Update statistics
        self._update_stats(command, user_id, username)
        
        hold_text = f"(held {self.movement_hold_duration}s)" if key in self.movement_keys else ""
        logger.info(f"{username:20} -> '{command:15}' => {key} {hold_text}")
    
    async def _press_key(self, key: str, duration: float = None):
        """Press a key for duration seconds"""
        duration = duration or self.press_duration
        
        try:
            if self.debug_mode:
                logger.debug(f"[DEBUG] Would press: {key} ({duration}s)")
                return
            
            self.keyboard.press(key)
            await asyncio.sleep(duration)
            self.keyboard.release(key)
            
        except Exception as e:
            logger.error(f"Error pressing key '{key}': {e}")
    
    async def _hold_key(self, key: str, duration: float):
        """Hold a key for duration seconds"""
        try:
            if self.debug_mode:
                logger.debug(f"[DEBUG] Would hold: {key} ({duration}s)")
                return
            
            self.keyboard.press(key)
            self.currently_pressed.add(key)
            await asyncio.sleep(duration)
            self.keyboard.release(key)
            self.currently_pressed.discard(key)
            
        except Exception as e:
            logger.error(f"Error holding key '{key}': {e}")
    
    async def _hold_multiple_keys(self, keys: list, duration: float):
        """Hold multiple keys together for duration seconds"""
        try:
            if self.debug_mode:
                logger.debug(f"[DEBUG] Would hold: {'+'.join(keys)} ({duration}s)")
                return
            
            # Press all keys
            for key in keys:
                self.keyboard.press(key)
                self.currently_pressed.add(key)
            
            # Hold for duration
            await asyncio.sleep(duration)
            
            # Release all keys
            for key in keys:
                self.keyboard.release(key)
                self.currently_pressed.discard(key)
            
        except Exception as e:
            logger.error(f"Error holding multiple keys {keys}: {e}")
    
    def _update_stats(self, command: str, user_id: str, username: str):
        """Update statistics"""
        self.stats["total_commands"] += 1
        self.stats["unique_users"].add(user_id)
        self.stats["total_users"] = len(self.stats["unique_users"])
        
        if command not in self.stats["commands_by_type"]:
            self.stats["commands_by_type"][command] = 0
        self.stats["commands_by_type"][command] += 1
    
    def _print_stats(self):
        """Print session statistics"""
        duration = datetime.now() - self.stats["start_time"]
        duration_seconds = duration.total_seconds()
        
        logger.info("\n" + "="*60)
        logger.info("RACING SESSION STATISTICS")
        logger.info("="*60)
        logger.info(f"Duration: {duration_seconds:.1f} seconds")
        logger.info(f"Total Commands: {self.stats['total_commands']}")
        logger.info(f"Unique Users: {self.stats['total_users']}")
        
        if duration_seconds > 0:
            cps = self.stats['total_commands'] / duration_seconds
            logger.info(f"Commands/Second: {cps:.2f}")
        
        if self.stats["commands_by_type"]:
            logger.info("\nTop Commands:")
            sorted_commands = sorted(
                self.stats["commands_by_type"].items(),
                key=lambda x: -x[1]
            )
            for command, count in sorted_commands[:10]:
                logger.info(f"  {command:15} x {count:3}")
        
        logger.info("="*60 + "\n")
    
    def add_mapping(self, command: str, key: str):
        """Add custom key mapping"""
        self.key_mapping[command.lower()] = key
        logger.info(f"[ADDED] mapping: '{command}' -> '{key}'")
    
    def remove_mapping(self, command: str):
        """Remove key mapping"""
        if command.lower() in self.key_mapping:
            del self.key_mapping[command.lower()]
            logger.info(f"[REMOVED] mapping: '{command}'")
    
    def set_cooldown(self, per_user_duration: float, global_duration: float = None):
        """Configure cooldown durations"""
        self.per_user_cooldown_duration = per_user_duration
        if global_duration:
            self.global_cooldown_duration = global_duration
        logger.info(f"[COOLDOWN] {per_user_duration}s per user, {global_duration or 'none'} global")
    
    def set_hold_duration(self, duration: float):
        """Configure movement key hold duration (for W/A/S/D)"""
        self.movement_hold_duration = duration
        logger.info(f"[HOLD] Movement keys (W/A/S/D) will be held for {duration}s")
    
    async def run(self):
        """Start the controller"""
        try:
            logger.info(f"[START] Racing Game Controller")
            logger.info(f"Target: @{self.unique_id}")
            logger.info(f"Debug Mode: {self.debug_mode}")
            logger.info(f"Waiting for stream to go live...")
            
            await self.client.connect()
            
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self._print_stats()
            await self.client.disconnect()
        
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            await self.client.disconnect()
    
    def run_blocking(self):
        """Run blocking (synchronous)"""
        try:
            logger.info(f"[START] Racing Game Controller (Blocking)")
            logger.info(f"Target: @{self.unique_id}")
            logger.info(f"Debug Mode: {self.debug_mode}")
            logger.info(f"Waiting for stream to go live...")
            
            self.client.run()
            
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self._print_stats()
        
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)


# ============== INTERACTIVE SETUP ==============

async def validate_stream_live(username: str, timeout: int = 10) -> bool:
    """
    Validate if TikTok stream is live
    
    Args:
        username: TikTok username
        timeout: Timeout in seconds
        
    Returns:
        True if stream is live, False otherwise
    """
    try:
        client = TikTokLiveClient(unique_id=username)
        is_live = await asyncio.wait_for(client.is_live(), timeout=timeout)
        return is_live
    except asyncio.TimeoutError:
        return False
    except Exception as e:
        logger.warning(f"Could not verify stream status: {e}")
        return False


def validate_username(username: str) -> bool:
    """
    Validate TikTok username format
    
    Args:
        username: TikTok username
        
    Returns:
        True if username format is valid
    """
    # Remove @ if present
    username = username.lstrip('@')
    
    # TikTok usernames: alphanumeric, underscore, period, 2-24 characters
    import re
    pattern = r'^[a-zA-Z0-9._]{2,24}$'
    
    is_valid = bool(re.match(pattern, username))
    return is_valid


async def pre_checklist():
    """
    Pre-flight checklist before setup
    
    Returns:
        Validated username or None if cancelled
    """
    print("\n" + "="*60)
    print("✅ PRE-FLIGHT CHECKLIST")
    print("="*60 + "\n")
    
    # === STEP 1: USERNAME VALIDATION ===
    print("📝 STEP 1: USERNAME VALIDATION")
    print("-" * 60)
    while True:
        username = input("Enter your TikTok username (without @): ").strip().lstrip('@')
        
        if not username:
            print("❌ Username cannot be empty!")
            continue
        
        if not validate_username(username):
            print("❌ Invalid username format!")
            print("   Rules: 2-24 characters, alphanumeric + underscore/period")
            continue
        
        print(f"✓ Username valid: @{username}\n")
        break
    
    # === STEP 2: CHECK IF STREAM IS LIVE ===
    print("🔴 STEP 2: CHECKING IF STREAM IS LIVE")
    print("-" * 60)
    print(f"Checking @{username}...")
    print("(This may take up to 10 seconds)\n")
    
    is_live = await validate_stream_live(username)
    
    if is_live:
        print(f"✅ Stream is LIVE! @{username} is currently streaming\n")
        return username
    else:
        print(f"⚠️  Stream is NOT LIVE or not accessible")
        print(f"   User @{username} might not be streaming right now\n")
        
        # Ask if user wants to continue anyway
        while True:
            choice = input("Continue anyway? (yes/no): ").strip().lower()
            if choice in ['yes', 'y']:
                print("⚠️  Controller will wait for stream to go live...\n")
                return username
            elif choice in ['no', 'n']:
                print("👋 Setup cancelled\n")
                return None
            else:
                print("❌ Please enter 'yes' or 'no'")


def get_user_input_safe(prompt: str, input_type=str, default=None, valid_options=None):
    """Get user input with validation"""
    while True:
        try:
            if default is not None:
                display_default = f" [{default}]" if default else ""
                user_input = input(f"{prompt}{display_default}: ").strip()
                if not user_input and default is not None:
                    return default
            else:
                user_input = input(f"{prompt}: ").strip()
            
            if not user_input:
                print("❌ Input cannot be empty!")
                continue
            
            if valid_options and user_input.lower() not in valid_options:
                print(f"❌ Please enter one of: {', '.join(valid_options)}")
                continue
            
            if input_type == bool:
                return user_input.lower() in ["yes", "y", "true", "1"]
            elif input_type == float:
                return float(user_input)
            elif input_type == int:
                return int(user_input)
            else:
                return user_input.lower()
        
        except ValueError:
            print(f"❌ Invalid input! Please enter a {input_type.__name__}")
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup cancelled")
            exit(0)


def save_config(config_data: dict, filename: str = "racing_config.json"):
    """Save configuration to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        logger.info(f"[CONFIG] Saved to {filename}")
        return True
    except Exception as e:
        logger.error(f"[CONFIG] Failed to save: {str(e)}")
        return False


def load_config(filename: str = "racing_config.json") -> dict | None:
    """Load configuration from JSON file"""
    try:
        if not os.path.exists(filename):
            return None
        
        with open(filename, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info(f"[CONFIG] Loaded from {filename}")
        return config
    except Exception as e:
        logger.error(f"[CONFIG] Failed to load: {str(e)}")
        return None


def interactive_setup(username: str = None):
    """Interactive setup menu"""
    print("\n" + "="*60)
    print("RACING GAME CONTROLLER - SETUP")
    print("="*60 + "\n")
    
    # === GAME NAME ===
    print("GAME SELECTION")
    print("-" * 60)
    game_name = get_user_input_safe("Enter game name (e.g., NFS HEAT, GTA V, Minecraft)")
    print(f"✓ Game: {game_name}\n")
    
    # === TIKTOK USERNAME ===
    if username is None:
        print("TIKTOK ACCOUNT")
        print("-" * 60)
        username = get_user_input_safe("Enter your TikTok username (without @)")
    
    print(f"TIKTOK ACCOUNT")
    print("-" * 60)
    print(f"✓ Username: @{username}\n")
    
    # === DEBUG MODE ===
    print("OPERATION MODE")
    print("-" * 60)
    print("Debug Mode: Safe testing (no actual keyboard input)")
    print("Production Mode: Real keyboard input to game")
    debug = get_user_input_safe(
        "Use Debug Mode? (yes/no)",
        input_type=bool,
        valid_options=["yes", "no", "y", "n"]
    )
    mode_text = "DEBUG MODE (Safe)" if debug else "PRODUCTION MODE (Real)"
    print(f"✓ Mode: {mode_text}\n")
    
    # === COOLDOWN ===
    print("⏱️  ANTI-SPAM SETTINGS")
    print("-" * 60)
    print("Cooldown prevents viewers from spamming commands")
    print("Recommended: 0.1-0.3 seconds")
    
    cooldown = get_user_input_safe(
        "Per-user cooldown duration (seconds)",
        input_type=float,
        default=0.2
    )
    print(f"✓ Cooldown: {cooldown}s per user\n")
    
    # === MOVEMENT KEY HOLD DURATION ===
    print("🎮 MOVEMENT KEY HOLD DURATION")
    print("-" * 60)
    print("When viewers press W/A/S/D, how long to hold the key?")
    print("Recommended: 3-5 seconds")
    print("(Other keys like SPACE, SHIFT will be pressed briefly)")
    
    hold_duration = get_user_input_safe(
        "Hold duration for W/A/S/D (seconds)",
        input_type=float,
        default=5.0
    )
    print(f"✓ Hold Duration: {hold_duration}s for W/A/S/D\n")
    
    # === CUSTOM MAPPINGS ===
    print("🎮 CUSTOM KEY MAPPINGS (Optional)")
    print("-" * 60)
    add_custom = get_user_input_safe(
        "Add custom key mappings? (yes/no)",
        input_type=bool,
        valid_options=["yes", "no", "y", "n"],
        default="no"
    )
    
    custom_mappings = {}
    if add_custom:
        print("\nEnter custom mappings (press Enter to skip):")
        print("Example: horn → h")
        while True:
            mapping_input = input("  Command → Key (or press Enter to done): ").strip()
            if not mapping_input:
                break
            
            if "→" not in mapping_input and "->" not in mapping_input:
                print("  ❌ Format: 'command → key' or 'command -> key'")
                continue
            
            try:
                sep = "→" if "→" in mapping_input else "->"
                cmd, key = mapping_input.split(sep)
                cmd = cmd.strip().lower()
                key = key.strip().lower()
                custom_mappings[cmd] = key
                print(f"  ✓ Added: {cmd} → {key}")
            except:
                print("  ❌ Invalid format. Try again.")
    
    print()
    
    # === SUMMARY ===
    print("="*60)
    print("✅ SETUP COMPLETE")
    print("="*60)
    print(f"Username:             @{username}")
    print(f"Mode:                 {mode_text}")
    print(f"Per-user Cooldown:    {cooldown}s")
    print(f"Movement Hold Time:   {hold_duration}s (for W/A/S/D)")
    if custom_mappings:
        print(f"Custom Mappings:      {len(custom_mappings)} added")
    print("="*60 + "\n")
    
    config_data = {
        "current_game": game_name,
        "username": username,
        "debug_mode": debug,
        "cooldown": cooldown,
        "hold_duration": hold_duration,
        "custom_mappings": custom_mappings
    }
    
    # Save config to JSON
    save_config(config_data, "config.json")
    
    return config_data


def main():
    """Main entry point"""
    
    # === PRE-CHECKLIST ===
    try:
        username = asyncio.run(pre_checklist())
        if username is None:
            return  # Cancelled by user
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled")
        return
    except Exception as e:
        logger.error(f"Checklist error: {e}")
        print(f"\n❌ Error during checklist: {e}")
        return
    
    # === INTERACTIVE SETUP ===
    config = interactive_setup(username)
    
    # === CREATE CONTROLLER ===
    controller = RacingGameController(
        unique_id=config["username"],
        debug_mode=config["debug_mode"]
    )
    
    # === APPLY CUSTOM SETTINGS ===
    if config["cooldown"] != 0.2:
        controller.set_cooldown(per_user_duration=config["cooldown"])
    
    if config["custom_mappings"]:
        print("🎮 Adding custom mappings...")
        for command, key in config["custom_mappings"].items():
            controller.add_mapping(command, key)
        print()
    
    # === RUN ===
    try:
        print("🚀 Starting Racing Game Controller...")
        print(f"Press Ctrl+C to stop\n")
        controller.run_blocking()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for playing!")


if __name__ == "__main__":
    main()
