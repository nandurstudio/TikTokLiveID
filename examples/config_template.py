"""
Configuration template for Chat-to-WASD Controller
Copy this file and customize for your setup
"""

# ============== MAIN CONFIG ==============

# TikTok username (without @)
TIKTOK_USERNAME = "nandurstudio"

# Debug mode: True = safe (no keyboard input), False = real (press keys)
DEBUG_MODE = True

# ============== KEY MAPPING ==============

# Default key mapping configuration
KEY_MAPPING = {
    # Movement keys
    "w": "w",
    "a": "a",
    "s": "s",
    "d": "d",
    
    # Indonesian aliases
    "maju": "w",      # forward
    "mundur": "s",    # backward
    "kiri": "a",      # left
    "kanan": "d",     # right
    
    # Jump/Action
    "jump": "space",
    "lompat": "space",
    
    # Attack/Interact
    "attack": "left",
    "serang": "left",
    "place": "right",
    "taruh": "right",
    
    # Game-specific (uncomment to add)
    # "sprint": "shift",
    # "crouch": "ctrl",
    # "interact": "e",
    # "menu": "esc",
}

# ============== COOLDOWN CONFIG ==============

# Default cooldown in seconds (prevents spam)
COOLDOWN_DURATION = 0.1

# Per-user cooldown enabled (prevents single user spamming)
ENABLE_USER_COOLDOWN = False
USER_COOLDOWN_DURATION = 0.5

# ============== LOGGING ==============

# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# Log file (set to None to disable file logging)
LOG_FILE = "chat_to_keys.log"

# ============== ADVANCED ==============

# Rate limit checks per minute (0 = disabled)
RATE_LIMIT = 0

# Whitelist users (set to None to allow all)
WHITELIST_USERS = None  # Example: ["user1", "user2"]

# Blacklist users
BLACKLIST_USERS = None  # Example: ["spammer1"]

# Filter by account age (days, 0 = disabled)
MIN_ACCOUNT_AGE = 0

# ============== OPTIONAL: GIFT REACTIONS ==============

# Gift rewards (setup for future feature)
GIFT_REACTIONS = {
    "Rose": "space",           # Rose = Jump
    "Gift": "e",               # Gift = Interact
    "Fireworks": "space",      # Fireworks = Big action
}

# ============== WEBSOCKET CONFIG ==============

# Connection retry attempts
MAX_RETRIES = 5

# Retry delay in seconds
RETRY_DELAY = 5

# Connection timeout in seconds
TIMEOUT = 30
