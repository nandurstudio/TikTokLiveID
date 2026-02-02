"""
TikTok Live Interactive Controller - Production Ready Script
Ready to connect to real TikTok streams
"""

import asyncio
import logging
from pynput.keyboard import Controller, Key
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent, DisconnectEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KeyboardController:
    """Handle keyboard input safely"""
    
    def __init__(self, debug_mode: bool = False):
        self.keyboard = Controller()
        self.debug_mode = debug_mode
        self.key_history = []
    
    async def press_key(self, key: str, duration: float = 0.1):
        """Press a key for duration seconds"""
        try:
            if self.debug_mode:
                logger.info(f"[DEBUG] Would press: {key}")
                return
            
            self.keyboard.press(key)
            await asyncio.sleep(duration)
            self.keyboard.release(key)
            self.key_history.append(key)
            logger.info(f"⌨️  Pressed: {key}")
        except Exception as e:
            logger.error(f"Error pressing key: {e}")


class ChatToKeyController:
    """Main controller for TikTok chat to keyboard mapping"""
    
    def __init__(self, unique_id: str, debug_mode: bool = False):
        self.unique_id = unique_id
        self.debug_mode = debug_mode
        self.client = TikTokLiveClient(unique_id=unique_id)
        self.keyboard = KeyboardController(debug_mode=debug_mode)
        
        # Key mapping configuration
        self.key_mapping = {
            # Movement
            "w": "w",
            "a": "a",
            "s": "s",
            "d": "d",
            
            # Indonesian aliases
            "maju": "w",
            "mundur": "s",
            "kiri": "a",
            "kanan": "d",
            
            # Actions
            "jump": "space",
            "lompat": "space",
            "attack": "left",
            "serang": "left",
            "place": "right",
            "taruh": "right",
        }
        
        # Cooldown tracking to prevent spam
        self.cooldowns = {}
        self.cooldown_duration = 0.1
        
        # Register event handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register event handlers"""
        @self.client.on(ConnectEvent)
        async def on_connect(event: ConnectEvent):
            logger.info(f"✅ Connected to @{event.unique_id} (Room ID: {self.client.room_id})")
        
        @self.client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            await self._handle_comment(event)
        
        @self.client.on(DisconnectEvent)
        async def on_disconnect(event: DisconnectEvent):
            logger.info("❌ Disconnected from stream")
    
    async def _handle_comment(self, event: CommentEvent):
        """Handle incoming comment"""
        command = event.comment.lower().strip()
        
        # Check if command is mapped
        key = self.key_mapping.get(command)
        if not key:
            return  # Ignore unmapped commands
        
        # Check cooldown
        if self._is_on_cooldown(command):
            return  # Ignore if on cooldown
        
        # Press the key
        await self.keyboard.press_key(key)
        self._set_cooldown(command)
        
        logger.info(f"👤 {event.user.nickname} -> {event.comment} ➜ {key}")
    
    def _is_on_cooldown(self, command: str) -> bool:
        """Check if command is on cooldown"""
        if command not in self.cooldowns:
            return False
        return asyncio.get_event_loop().time() < self.cooldowns[command]
    
    def _set_cooldown(self, command: str):
        """Set cooldown for command"""
        self.cooldowns[command] = asyncio.get_event_loop().time() + self.cooldown_duration
    
    def add_mapping(self, command: str, key: str):
        """Add custom mapping"""
        self.key_mapping[command.lower()] = key
        logger.info(f"Added mapping: {command} -> {key}")
    
    async def start(self):
        """Start the controller"""
        try:
            logger.info(f"🚀 Starting controller for @{self.unique_id}")
            logger.info(f"Debug mode: {self.debug_mode}")
            await self.client.connect()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            await self.client.disconnect()
        except Exception as e:
            logger.error(f"Error: {e}")
    
    def run(self):
        """Run the controller (blocking)"""
        try:
            logger.info(f"🚀 Starting controller for @{self.unique_id}")
            logger.info(f"Debug mode: {self.debug_mode}")
            self.client.run()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Error: {e}")


if __name__ == "__main__":
    # Configuration
    TIKTOK_USERNAME = "nandurstudio"  # Change to your TikTok username (without @)
    DEBUG_MODE = True  # Set to False for real keyboard input
    
    # Create and run controller
    controller = ChatToKeyController(
        unique_id=TIKTOK_USERNAME,
        debug_mode=DEBUG_MODE
    )
    
    # Optional: Add custom mappings
    # controller.add_mapping("maju", "w")
    # controller.add_mapping("mundur", "s")
    
    # Start
    controller.run()
