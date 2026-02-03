"""
TikTok Live Racing Game Controller
Real-time WASD control from TikTok live chat

Supports racing games like:
- Minecraft Racing
- GTA
- Roblox Racing
- Need for Speed
- Any game with WASD controls

@nandurstudio
Date Created: 2025-12-15
Last Modified: 2026-02-03
"""

import asyncio
import logging
import sys
import io
import json
import os
import time
import traceback
import httpx
from pynput.keyboard import Controller, Key
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent, DisconnectEvent, GiftEvent, LikeEvent
from typing import Dict, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from notification_logger import NotificationLogger, OverlayNotificationManager
from ipc_server import start_ipc_server

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configure logging with UTF-8 support
logging.basicConfig(
    level=logging.INFO,  # Back to INFO level
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('racing_controller.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Disable noisy HTTP logs from httpx and urllib3
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

# Suppress asyncio pending task warnings (normal during shutdown)
logging.getLogger('asyncio').setLevel(logging.CRITICAL)

# Notification system
overlay_notif_manager = OverlayNotificationManager()
notify = NotificationLogger(overlay_callback=overlay_notif_manager.send)


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
    
    def __init__(self, unique_id: str, debug_mode: bool = True, game_name: str = "Game", custom_mappings: dict = None):
        """
        Initialize racing game controller
        
        Args:
            unique_id: TikTok username (without @)
            debug_mode: True = no keyboard input, False = real keyboard
            game_name: Name of the game being played (for logging)
            custom_mappings: Custom command mappings from config.json
        """
        self.unique_id = unique_id
        self.debug_mode = debug_mode
        self.game_name = game_name
        self.custom_mappings = custom_mappings or {}  # Store for animation detection
        
        # Anti-block: Use longer timeout to avoid connection issues
        # Don't override default headers - TikTokLive library handles this smartly
        httpx_kwargs = {
            "timeout": httpx.Timeout(60.0, connect=15.0, read=45.0),
            "follow_redirects": True,
        }
        
        # WebSocket with retry-friendly settings
        ws_kwargs = {
            "ping_interval": 10,
            "ping_timeout": 30,
            "close_timeout": 10,
        }
        
        # TikTok client with anti-block settings
        web_kwargs = {
            "httpx_kwargs": httpx_kwargs
        }
        
        self.client = TikTokLiveClient(
            unique_id=unique_id,
            web_kwargs=web_kwargs,
            ws_kwargs=ws_kwargs
        )
        
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
        
        # Animation state tracking
        self.active_animations = {
            'gas': None,        # Current gas animation task
            'brake': None,      # Current brake animation task
            'steer_left': None, # Current steer left animation task
            'steer_right': None # Current steer right animation task
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
        
        # Start IPC server for Electron overlay communication
        self._start_ipc_server()
    
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
        
        @self.client.on(GiftEvent)
        async def on_gift(event: GiftEvent):
            await self._handle_gift_event(event)
        
        @self.client.on(LikeEvent)
        async def on_like(event: LikeEvent):
            await self._handle_like_event(event)
    
    def _start_ipc_server(self):
        """Start IPC server for Electron overlay communication"""
        try:
            ipc_server = start_ipc_server()
            logger.info("✅ IPC Server started on http://127.0.0.1:9999/ipc")
        except Exception as e:
            logger.warning(f"⚠️ Failed to start IPC server: {e}")
            logger.info("Continuing without overlay communication...")
    
    async def _handle_comment(self, event: CommentEvent):
        """Handle incoming comment"""
        command = event.comment.lower().strip()
        user_id = event.user.unique_id
        username = event.user.nickname
        
        # Check if command exists in custom_mappings
        mapped_keys = self.custom_mappings.get(command, [])
        
        # Track if animation was triggered (to avoid double log)
        animation_triggered = False
        
        # Initialize key counts
        w_count = 0
        s_count = 0
        a_count = 0
        d_count = 0
        space_count = 0
        c_count = 0
        
        # Analyze mapped keys to determine animation type
        if mapped_keys and len(mapped_keys) > 0:
            # Count different key types
            w_count = mapped_keys.count('w')
            s_count = mapped_keys.count('s')
            a_count = mapped_keys.count('a')
            d_count = mapped_keys.count('d')
            space_count = mapped_keys.count('space')
            c_count = mapped_keys.count('c')
            
            # GAS PEDAL: Contains 'w' key(s)
            if w_count > 0:
                intensity = min(w_count, 4)  # Max 4
                try:
                    overlay_notif_manager.send_event('gas-event', {
                        'username': username,
                        'intensity': intensity,
                        'command': command
                    })
                    animation_triggered = True
                except Exception as ipc_err:
                    logger.debug(f"IPC gas event error: {ipc_err}")
            
            # BRAKE PEDAL: Contains 's' key(s)
            if s_count > 0:
                intensity = min(s_count, 4)  # Max 4
                try:
                    overlay_notif_manager.send_event('brake-event', {
                        'username': username,
                        'intensity': intensity,
                        'command': command
                    })
                    animation_triggered = True
                except Exception as ipc_err:
                    logger.debug(f"IPC brake event error: {ipc_err}")
            
            # STEERING LEFT: Contains 'a' key
            if a_count > 0:
                try:
                    overlay_notif_manager.send_event('steer-left-event', {
                        'username': username,
                        'command': command
                    })
                    animation_triggered = True
                except Exception as ipc_err:
                    logger.debug(f"IPC steer-left event error: {ipc_err}")
            
            # STEERING RIGHT: Contains 'd' key
            if d_count > 0:
                try:
                    overlay_notif_manager.send_event('steer-right-event', {
                        'username': username,
                        'command': command
                    })
                    animation_triggered = True
                except Exception as ipc_err:
                    logger.debug(f"IPC steer-right event error: {ipc_err}")
            
            # DRIFT BUTTON: Contains 'space' key
            if space_count > 0:
                try:
                    overlay_notif_manager.send_event('drift-event', {
                        'username': username,
                        'command': command
                    })
                    animation_triggered = True
                except Exception as ipc_err:
                    logger.debug(f"IPC drift event error: {ipc_err}")
            
            # CAMERA BUTTON: Contains 'c' key
            if c_count > 0:
                try:
                    overlay_notif_manager.send_event('camera-event', {
                        'username': username,
                        'command': command
                    })
                    animation_triggered = True
                except Exception as ipc_err:
                    logger.debug(f"IPC camera event error: {ipc_err}")
        
        # Log command if animation was triggered (for multi-key commands)
        if animation_triggered:
            # Reconstruct the display text based on what was triggered
            display_keys = []
            if w_count > 0:
                display_keys.append(f"{w_count}x W")
            if s_count > 0:
                display_keys.append(f"{s_count}x S")
            if a_count > 0:
                display_keys.append(f"{a_count}x A")
            if d_count > 0:
                display_keys.append(f"{d_count}x D")
            if space_count > 0:
                display_keys.append("SPACE")
            if c_count > 0:
                display_keys.append("C")
            
            keys_text = " + ".join(display_keys)
            logger.info(f"[{username}] {command} \u2192 {keys_text}")
        
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
            
            keys_text = " + ".join([k.upper() for k in combination])
            logger.info(f"[{username}] {command} → {keys_text}")
            
            # Hold multiple keys simultaneously
            await self._hold_multiple_keys(combination, self.movement_hold_duration)
            user_cooldown.reset()
            
            # Update statistics
            self._update_stats(command, user_id, username)
            
            # Single notification call
            notify.command_received(username, command, keys_text)
            return
        
        # Check if command is mapped
        key = self.key_mapping.get(command)
        if not key:
            return  # Ignore unmapped commands
        
        # Check per-user cooldown
        if user_cooldown.is_on_cooldown():
            return  # Ignore if too fast
        
        # Handle key as list (from config.json) or string (from default mapping)
        if isinstance(key, list):
            # If it's a list with multiple keys, treat as combination or special command
            if len(key) > 1:
                # Check if it's a special command type
                if key[0].startswith('_'):
                    # Special command - just log and ignore (handled elsewhere)
                    user_cooldown.reset()
                    self._update_stats(command, user_id, username)
                    notify.command_received(username, command, f"[{key[0]}]")
                    return
                
                # Check if it's a multi-press (all same key) or combination (different keys)
                if all(k == key[0] for k in key):
                    # Multi-press: Hold same key N times for duration each
                    keys_text = f"{len(key)}x {key[0].upper()}"
                    key_count = len(key)
                    
                    # Only log and execute if animation was NOT already triggered
                    if not animation_triggered:
                        logger.info(f"[{username}] {command} → {keys_text}")
                        
                        # For movement keys (w/a/s/d), hold multiple times
                        # For other keys, just press once
                        if key[0] in self.movement_keys:
                            await self._hold_key_multiple_times(key[0], key_count, self.movement_hold_duration)
                        else:
                            await self._press_key(key[0])
                        
                        notify.command_received(username, command, keys_text)
                    
                    user_cooldown.reset()
                    self._update_stats(command, user_id, username)
                    return
                else:
                    # Combination: Different keys (may need sequential or simultaneous execution)
                    keys_text = " + ".join([k.upper() for k in key])
                    
                    # Only log and execute if animation was NOT already triggered
                    if not animation_triggered:
                        logger.info(f"[{username}] {command} → {keys_text}")
                        # Use smart execution: sequential for conflicts, simultaneous for non-conflicts
                        await self._execute_sequential_keys(key, self.movement_hold_duration)
                        notify.command_received(username, command, keys_text)
                    
                    user_cooldown.reset()
                    self._update_stats(command, user_id, username)
                    return
            # If it's a single-item list, extract the string
            elif len(key) == 1:
                key = key[0]
            else:
                return  # Empty list, ignore
        
        # Now key is guaranteed to be a string
        # Special keys starting with _ are handled dynamically via custom_mappings
        # No hardcoded behavior needed - just skip to normal key processing
        
        # Skip if animation already triggered (to avoid double/triple log)
        if animation_triggered:
            user_cooldown.reset()
            self._update_stats(command, user_id, username)
            # Don't call notify here - already logged in animation block above
            return
        
        # Always log single key commands (only if animation NOT triggered)
        logger.info(f"[{username}] {command} → {key.upper()}")
        
        # Check for specific single keys that need animation
        # Only send if animation was NOT already triggered by detection phase
        if not animation_triggered:
            if key == 'c':
                # Camera button animation
                try:
                    overlay_notif_manager.send_event('camera-event', {
                        'username': username,
                        'command': command
                    })
                except Exception as ipc_err:
                    logger.error(f"IPC camera event error: {ipc_err}")
            elif key == 'space':
                # Drift button animation
                try:
                    overlay_notif_manager.send_event('drift-event', {
                        'username': username,
                        'command': command
                    })
                except Exception as ipc_err:
                    logger.debug(f"IPC drift event error: {ipc_err}")
        
        # Determine if this key should be held or pressed
        # Special keys that need animation: c (camera), space (drift)
        if key in ['c', 'space']:
            # Hold for full duration (like movement keys)
            await self._hold_key(key, self.movement_hold_duration)
        elif key in self.movement_keys:
            # Hold movement keys for configured duration
            await self._hold_key(key, self.movement_hold_duration)
        else:
            # Press other keys briefly
            await self._press_key(key)
        
        user_cooldown.reset()
        
        # Update statistics
        self._update_stats(command, user_id, username)
        
        # Single notification call
        notify.command_received(username, command, key.upper())
    
    async def _handle_gift_event(self, event: GiftEvent):
        """Handle incoming gift event (e.g., rose/bunga mawar for NOS)"""
        try:
            # Check if this is a rose/bunga mawar gift (usually gift_id 1 or similar)
            # Rose gift typically has name containing "rose" or "mawar"
            # event.gift is already ExtendedGift object with .name attribute
            gift_name = event.gift.name.lower() if hasattr(event.gift, 'name') else ""
            
            # Detect rose/mawar gift
            if "rose" in gift_name or "mawar" in gift_name:
                user_id = event.user.unique_id
                username = event.user.nickname
                
                # Get or create user cooldown
                if user_id not in self.user_cooldowns:
                    self.user_cooldowns[user_id] = UserCooldown(
                        cooldown_duration=self.per_user_cooldown_duration
                    )
                
                user_cooldown = self.user_cooldowns[user_id]
                
                # Check per-user cooldown
                if user_cooldown.is_on_cooldown():
                    return  # Ignore if too fast
                
                # Send IPC message to overlay to trigger NOS animation
                try:
                    overlay_notif_manager.send_event('gift-event', {
                        'gift_name': gift_name,
                        'username': username
                    })
                    logger.info(f"🌹 IPC gift-event sent for {username}")
                except Exception as ipc_err:
                    logger.warning(f"⚠️ IPC gift event error: {ipc_err}")
                
                # Trigger NOS/Nitro - read from config mapping
                # Get mapped keys for _gift_rose from config
                mapped_keys = self.custom_mappings.get('_gift_rose', [])
                for key in mapped_keys:
                    await self._press_key(key, 0.5)
                
                user_cooldown.reset()
                self._update_stats('gift_rose', user_id, username)
                notify.command_received(username, "gift_rose", "ROSE GIFT 🌹")
        
        except Exception as e:
            logger.error(f"Error handling gift event: {e}")
    
    async def _handle_like_event(self, event: LikeEvent):
        """Handle incoming like event (love/heart taps for TAP)"""
        try:
            user_id = event.user.unique_id
            username = event.user.nickname
            
            # Get or create user cooldown
            if user_id not in self.user_cooldowns:
                self.user_cooldowns[user_id] = UserCooldown(
                    cooldown_duration=self.per_user_cooldown_duration
                )
            
            user_cooldown = self.user_cooldowns[user_id]
            
            # Check per-user cooldown
            if user_cooldown.is_on_cooldown():
                return  # Ignore if too fast
            
            # Send IPC message to overlay to trigger KLAKSON animation
            try:
                overlay_notif_manager.send_event('like-event', {
                    'username': username
                })
            except Exception as ipc_err:
                logger.debug(f"IPC like event error: {ipc_err}")
            
            # Trigger horn/klakson - read from config mapping
            # Get mapped keys for _like_love from config
            mapped_keys = self.custom_mappings.get('_like_love', [])
            for key in mapped_keys:
                await self._press_key(key, 0.2)
            
            user_cooldown.reset()
            self._update_stats('like_love', user_id, username)
            notify.command_received(username, "like_love", "LIKE/LOVE ❤️")
        
        except Exception as e:
            logger.error(f"Error handling like event: {e}")
    
    async def _press_key(self, key: str, duration: float = None):
        """Press a key for duration seconds"""
        duration = duration or self.press_duration
        
        try:
            if self.debug_mode:
                logger.debug(f"[DEBUG] Would press: {key} ({duration}s)")
                return
            
            # Map special key names to pynput Key objects
            if key == 'space':
                key = Key.space
            elif key == 'enter':
                key = Key.enter
            elif key == 'shift':
                key = Key.shift
            elif key == 'ctrl' or key == 'lctrl':
                key = Key.ctrl_l
            
            self.keyboard.press(key)
            await asyncio.sleep(duration)
            self.keyboard.release(key)
            
        except Exception as e:
            logger.error(f"Error pressing key '{key}': {e}")
    
    def _are_keys_conflicting(self, keys: list) -> bool:
        """Check if keys conflict (can't be held simultaneously)
        
        Conflicting pairs:
        - W + S (forward + backward)
        - A + D (left + right)
        
        Non-conflicting (can simultaneous):
        - W + A (forward + left)
        - W + D (forward + right)
        - S + A (backward + left)
        - S + D (backward + right)
        """
        has_forward = 'w' in keys
        has_backward = 's' in keys
        has_left = 'a' in keys
        has_right = 'd' in keys
        
        # Check for conflicting pairs
        if has_forward and has_backward:
            return True  # W + S conflict
        if has_left and has_right:
            return True  # A + D conflict
        
        return False  # Non-conflicting
    
    async def _execute_sequential_keys(self, keys: list, duration: float):
        """Execute keys sequentially if they conflict, simultaneously if not
        
        Example:
        - ["w", "a"] → simultaneous (non-conflict)
        - ["w", "s"] → sequential (conflict: W first, then S)
        """
        if self._are_keys_conflicting(keys):
            # Conflicting keys: execute sequentially
            logger.debug(f"Executing conflicting keys sequentially: {keys}")
            for key in keys:
                # Stop any running animation for this key
                if key == 'w':
                    animation_type = 'gas'
                elif key == 's':
                    animation_type = 'brake'
                elif key == 'a':
                    animation_type = 'steer_left'
                elif key == 'd':
                    animation_type = 'steer_right'
                else:
                    continue
                
                # Cancel previous animation if exists
                if self.active_animations[animation_type]:
                    self.active_animations[animation_type].cancel()
                
                # Execute current key
                await self._hold_key(key, duration)
                
                # Small delay between sequential presses
                await asyncio.sleep(0.05)
        else:
            # Non-conflicting keys: execute simultaneously
            logger.debug(f"Executing non-conflicting keys simultaneously: {keys}")
            
            # Map special key names
            mapped_keys = []
            for key in keys:
                if key == 'space':
                    mapped_keys.append(Key.space)
                elif key == 'enter':
                    mapped_keys.append(Key.enter)
                elif key == 'shift':
                    mapped_keys.append(Key.shift)
                elif key == 'ctrl' or key == 'lctrl':
                    mapped_keys.append(Key.ctrl_l)
                else:
                    mapped_keys.append(key)
            
            # Press all simultaneously
            for key in mapped_keys:
                self.keyboard.press(key)
                self.currently_pressed.add(key)
            
            # Hold for duration
            await asyncio.sleep(duration)
            
            # Release all
            for key in mapped_keys:
                self.keyboard.release(key)
                self.currently_pressed.discard(key)
    
    async def _hold_key_multiple_times(self, key: str, count: int, duration: float):
        """Hold a key multiple times, each for duration seconds
        
        Args:
            key: Key to hold
            count: Number of times to hold (e.g., "aaa" = 3 times)
            duration: Duration to hold each time (default 3 seconds)
        
        Example: "aaa" → Hold A for 3s, release, hold A for 3s, release, hold A for 3s (total ~9s)
        """
        try:
            if self.debug_mode:
                logger.debug(f"[DEBUG] Would hold {count}x: {key} ({duration}s each)")
                return
            
            # Map special key names to pynput Key objects
            mapped_key = key
            if key == 'space':
                mapped_key = Key.space
            elif key == 'enter':
                mapped_key = Key.enter
            elif key == 'shift':
                mapped_key = Key.shift
            elif key == 'ctrl' or key == 'lctrl':
                mapped_key = Key.ctrl_l
            
            # Hold key N times
            for i in range(count):
                self.keyboard.press(mapped_key)
                self.currently_pressed.add(key)
                await asyncio.sleep(duration)
                self.keyboard.release(mapped_key)
                self.currently_pressed.discard(key)
                
                # Small delay between presses (except last one)
                if i < count - 1:
                    await asyncio.sleep(0.05)  # 50ms delay between presses
        
        except Exception as e:
            logger.error(f"Error holding key multiple times '{key}' ({count}x): {e}")
    
    async def _hold_key(self, key: str, duration: float):
        """Hold a key for duration seconds"""
        try:
            if self.debug_mode:
                logger.debug(f"[DEBUG] Would hold: {key} ({duration}s)")
                return
            
            # Map special key names to pynput Key objects
            if key == 'space':
                key = Key.space
            elif key == 'enter':
                key = Key.enter
            elif key == 'shift':
                key = Key.shift
            elif key == 'ctrl' or key == 'lctrl':
                key = Key.ctrl_l
            
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
            
            # Map special key names to pynput Key objects
            mapped_keys = []
            for key in keys:
                if key == 'space':
                    mapped_keys.append(Key.space)
                elif key == 'enter':
                    mapped_keys.append(Key.enter)
                elif key == 'shift':
                    mapped_keys.append(Key.shift)
                elif key == 'ctrl' or key == 'lctrl':
                    mapped_keys.append(Key.ctrl_l)
                else:
                    mapped_keys.append(key)
            
            # Press all keys simultaneously
            for key in mapped_keys:
                self.keyboard.press(key)
                self.currently_pressed.add(key)
            
            # Hold for duration
            await asyncio.sleep(duration)
            
            # Release all keys
            for key in mapped_keys:
                self.keyboard.release(key)
                self.currently_pressed.discard(key)
            
        except Exception as e:
            logger.error(f"Error holding multiple keys {keys}: {e}")
    
    async def _press_keys_sequentially(self, keys: list, delay: float = 0.05):
        """Press multiple keys sequentially (one after another)
        
        Args:
            keys: List of keys to press
            delay: Delay between key presses in seconds (default 50ms)
        """
        try:
            if self.debug_mode:
                logger.debug(f"[DEBUG] Would press sequentially: {len(keys)}x {keys[0]}")
                return
            
            # Press each key one after another with delay
            for key in keys:
                self.keyboard.press(key)
                await asyncio.sleep(self.press_duration)  # Hold key briefly
                self.keyboard.release(key)
                
                # Delay between sequential presses
                if key != keys[-1]:  # Don't delay after last press
                    await asyncio.sleep(delay)
            
        except Exception as e:
            logger.error(f"Error pressing keys sequentially {keys}: {e}")
    
    def _update_stats(self, command: str, user_id: str, username: str):
        """Update statistics"""
        self.stats["total_commands"] += 1
        self.stats["unique_users"].add(user_id)
        self.stats["total_users"] = len(self.stats["unique_users"])
        
        if command not in self.stats["commands_by_type"]:
            self.stats["commands_by_type"][command] = 0
        self.stats["commands_by_type"][command] += 1
        
        if command not in self.stats["commands_by_type"]:
            self.stats["commands_by_type"][command] = 0
        self.stats["commands_by_type"][command] += 1
    
    async def _cleanup_async(self):
        """Async cleanup for proper websocket disconnection"""
        try:
            # Cancel pending animations
            for anim_type, task in self.active_animations.items():
                if task:
                    try:
                        task.cancel()
                    except:
                        pass
            
            # Close client connection properly (async)
            if self.client and self.client.connected:
                try:
                    await self.client.disconnect()
                    # Give websocket time to close cleanly
                    await asyncio.sleep(0.3)
                except:
                    pass
            
            # Cancel all remaining tasks
            try:
                tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
                for task in tasks:
                    task.cancel()
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
            except:
                pass
            
            logger.info("[CLEANUP] Resources released successfully")
        except Exception as e:
            logger.debug(f"Cleanup error (non-critical): {e}")
    
    def _cleanup(self):
        """Synchronous cleanup wrapper"""
        try:
            # Try to run async cleanup if event loop is available
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, schedule async cleanup
                asyncio.ensure_future(self._cleanup_async())
            else:
                # If loop is not running, run async cleanup in new loop
                asyncio.run(self._cleanup_async())
        except RuntimeError:
            # No event loop available, do basic cleanup only
            logger.debug("[CLEANUP] No event loop, skipping async cleanup")
            pass
    
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
        """Run blocking (synchronous) with retry logic for anti-block"""
        max_retries = 5
        retry_count = 0
        base_delay = 10  # Start with 10 seconds for first retry
        initial_delay = 2  # Initial delay before first connection
        
        # Wait a bit before first connection to avoid burst pattern
        if initial_delay > 0:
            logger.info(f"⏳ Waiting {initial_delay}s before connecting (anti-block delay)...")
            time.sleep(initial_delay)
        
        while retry_count < max_retries:
            try:
                logger.info(f"[START] Racing Game Controller (Blocking)")
                logger.info(f"Target: @{self.unique_id}")
                logger.info(f"Debug Mode: {self.debug_mode}")
                logger.info(f"Waiting for stream to go live...")
                
                self.client.run()
                break  # Success, exit retry loop
                
            except KeyboardInterrupt:
                logger.info("✅ Goodbye!")
                self._print_stats()
                # Proper async cleanup to prevent websocket errors
                try:
                    asyncio.run(self._cleanup_async())
                except:
                    pass  # Ignore any cleanup errors on exit
                break
            
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a blocking-related error
                is_blocked = any([
                    "DEVICE_BLOCKED" in error_msg,
                    "blocked" in error_msg.lower(),
                    "SIGI_STATE" in error_msg,
                    "UnicodeDecodeError" in error_msg,
                    "'utf-8' codec can't decode" in error_msg,
                ])
                
                if is_blocked:
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.error(f"❌ Maximum retries ({max_retries}) reached. Cannot bypass block.")
                        logger.error("💡 Try these solutions:")
                        logger.error("   1. Wait 30-60 minutes before trying again")
                        logger.error("   2. Use MOCK mode for testing (no TikTok connection)")
                        logger.error("   3. Try from a different network/IP address")
                        logger.error("   4. Use VPN or proxy")
                        logger.error("   5. Contact library maintainer for sign_api_key")
                        self._print_stats()
                        raise
                    
                    # Exponential backoff
                    delay = base_delay * (2 ** (retry_count - 1))
                    logger.warning(f"⚠️  TikTok blocking detected. Retry {retry_count}/{max_retries} in {delay}s...")
                    logger.info(f"💡 Rotating session and waiting...")
                    time.sleep(delay)
                    
                    # Recreate client with new session
                    logger.info("🔄 Creating new session...")
                    old_debug = self.debug_mode
                    old_game = self.game_name
                    self.__init__(self.unique_id, old_debug, old_game)
                else:
                    # Other errors, log and raise
                    logger.error(f"Error: {e}")
                    logger.error(traceback.format_exc())
                    self._print_stats()
                    raise
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
