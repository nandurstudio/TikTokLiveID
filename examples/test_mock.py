"""
TikTok Live Interactive Controller - Mock Testing Script
Safe testing without risking TikTok ban

Run this to test the keyboard mapping logic and event handling
without connecting to real TikTok streams.
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, Callable
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class MockUser:
    """Mock TikTok User"""
    unique_id: str
    nickname: str
    
    def __repr__(self):
        return f"User({self.nickname})"


@dataclass
class MockCommentEvent:
    """Mock Comment Event from TikTok"""
    user: MockUser
    comment: str
    
    def __repr__(self):
        return f"[{self.user.nickname}]: {self.comment}"


class KeyMapping:
    """Handles command to key mapping"""
    
    def __init__(self):
        self.mapping: Dict[str, str] = {
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
            "attack": "left_click",
            "serang": "left_click",
            "place": "right_click",
            "taruh": "right_click",
        }
        
        # Cooldown tracking
        self.cooldowns: Dict[str, float] = {}
        self.cooldown_duration = 0.2  # seconds
    
    def get_key(self, command: str) -> str | None:
        """Get mapped key for a command (case-insensitive)"""
        return self.mapping.get(command.lower())
    
    def set_cooldown(self, command: str, duration: float = None):
        """Set cooldown for a command"""
        self.cooldowns[command] = asyncio.get_event_loop().time() + (duration or self.cooldown_duration)
    
    def is_on_cooldown(self, command: str) -> bool:
        """Check if command is on cooldown"""
        if command not in self.cooldowns:
            return False
        return asyncio.get_event_loop().time() < self.cooldowns[command]
    
    def add_mapping(self, command: str, key: str):
        """Add or update a mapping"""
        self.mapping[command.lower()] = key
        logger.info(f"✓ Added mapping: '{command}' -> '{key}'")


class MockTikTokLiveClient:
    """Mock TikTok Live Client for testing"""
    
    def __init__(self, debug_mode: bool = True):
        self.key_mapping = KeyMapping()
        self.debug_mode = debug_mode
        self.event_handlers: Dict[str, list] = {}
        self.connected = False
        
    def on_comment(self, handler: Callable):
        """Decorator to register comment handler"""
        if "comment" not in self.event_handlers:
            self.event_handlers["comment"] = []
        self.event_handlers["comment"].append(handler)
        return handler
    
    async def simulate_comment(self, username: str, nickname: str, comment: str):
        """Simulate a comment event"""
        event = MockCommentEvent(
            user=MockUser(unique_id=username, nickname=nickname),
            comment=comment
        )
        
        logger.info(f"📨 Incoming: {event}")
        
        if "comment" in self.event_handlers:
            for handler in self.event_handlers["comment"]:
                await handler(event)
    
    async def simulate_stream(self, test_messages: list):
        """Simulate a stream with multiple messages"""
        logger.info("🔴 [MOCK LIVE STARTED]")
        self.connected = True
        
        for i, (username, nickname, comment) in enumerate(test_messages, 1):
            logger.info(f"Message {i}/{len(test_messages)}")
            await self.simulate_comment(username, nickname, comment)
            await asyncio.sleep(0.5)  # Simulate delay between messages
        
        logger.info("🔴 [MOCK LIVE ENDED]")
        self.connected = False


class KeyboardSimulator:
    """Simulates keyboard presses (without actually pressing keys)"""
    
    def __init__(self, debug_mode: bool = True):
        self.debug_mode = debug_mode
        self.key_history = []
    
    async def press_key(self, key: str, duration: float = 0.1):
        """Simulate pressing a key"""
        self.key_history.append((key, duration))
        
        if self.debug_mode:
            logger.info(f"⌨️  [KEY PRESS] {key} ({duration}s)")
        else:
            logger.info(f"⌨️  Actually pressing: {key}")
            # In real mode, would use pynput here
    
    def get_history(self):
        """Get all key presses"""
        return self.key_history
    
    def print_summary(self):
        """Print summary of all key presses"""
        logger.info("\n📊 KEY PRESS SUMMARY:")
        logger.info(f"Total presses: {len(self.key_history)}")
        
        key_count = {}
        for key, _ in self.key_history:
            key_count[key] = key_count.get(key, 0) + 1
        
        for key, count in sorted(key_count.items(), key=lambda x: -x[1]):
            logger.info(f"  {key}: {count}x")


# ============== EXAMPLE TEST SCRIPT ==============

async def main():
    """Run mock testing"""
    
    logger.info("=" * 60)
    logger.info("TikTok Live Chat-to-WASD Controller - Mock Testing")
    logger.info("=" * 60)
    
    # Initialize
    client = MockTikTokLiveClient(debug_mode=True)
    keyboard = KeyboardSimulator(debug_mode=True)
    
    # Configure key mapping
    logger.info("\n🔧 Configuring Key Mapping...")
    client.key_mapping.add_mapping("w", "w")
    client.key_mapping.add_mapping("maju", "w")
    client.key_mapping.add_mapping("a", "a")
    client.key_mapping.add_mapping("s", "s")
    client.key_mapping.add_mapping("d", "d")
    client.key_mapping.add_mapping("jump", "space")
    client.key_mapping.add_mapping("lompat", "space")
    
    # Register comment handler
    @client.on_comment
    async def handle_comment(event: MockCommentEvent):
        """Handle incoming comments"""
        command = event.comment.lower().strip()
        key = client.key_mapping.get_key(command)
        
        if key:
            if client.key_mapping.is_on_cooldown(command):
                logger.warning(f"⏱️  COOLDOWN: Ignoring '{command}' (on cooldown)")
                return
            
            await keyboard.press_key(key)
            client.key_mapping.set_cooldown(command)
        else:
            logger.debug(f"❌ Unknown command: '{command}'")
    
    # Test messages
    test_messages = [
        ("user123", "Adi", "w"),
        ("user456", "Budi", "maju"),
        ("user789", "Citra", "a"),
        ("user101", "Dedi", "kanan"),
        ("user202", "Eka", "jump"),
        ("user303", "Fajar", "lompat"),
        ("user404", "Gina", "unknown_command"),
        ("user505", "Hendra", "s"),
        ("user606", "Ira", "w"),
        ("user707", "Joko", "w"),  # Test cooldown
    ]
    
    # Run mock stream
    logger.info("\n📹 Starting mock live stream...\n")
    await client.simulate_stream(test_messages)
    
    # Print summary
    logger.info("")
    keyboard.print_summary()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Mock testing completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
