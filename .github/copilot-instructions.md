# TikTokLive Python Library - AI Coding Agent Instructions

## Project Overview
This is a Python library for connecting to TikTok's LIVE service to receive real-time livestream events (comments, gifts, joins, etc.) via TikTok's internal Webcast push service. It's a reverse-engineered implementation—not an official API.

## Architecture

### Core Components
- **`TikTokLive/client/`**: Client implementation with dual connection modes
  - `client.py`: High-level `TikTokLiveClient` with event handling & message parsing
  - `base.py`: `BaseClient` handles websocket/polling connections, room management
  - `config.py`: Default HTTP params & headers mimicking browser behavior
  - `httpx.py`: HTTP client wrapper for TikTok API requests
- **`TikTokLive/types/`**: Event schemas & data objects
  - `events.py`: All event classes (CommentEvent, GiftEvent, etc.) inherit from `AbstractEvent`
  - `objects.py`: Data structures (User, Gift, Avatar, etc.)
  - `errors.py`: Custom exceptions for connection failures
- **`TikTokLive/proto/`**: Protobuf message handling
  - `tiktok_schema_pb2.py`: Generated protobuf definitions (don't edit manually)
  - `utilities.py`: Deserializes binary protobuf messages to dicts

### Connection Flow
1. Client connects using `unique_id` (TikTok username)
2. Initial HTTP request to `webcast/fetch/` establishes room connection
3. If available, upgrades to websocket via `wsUrl` + `wsParam` from response
4. Falls back to long polling (`im/fetch/`) if websocket unavailable
5. Cursor-based pagination: `cursor` param tracks message position

## Key Patterns

### Event-Driven Architecture
```python
# Decorator pattern for event handlers
@client.on("comment")
async def on_comment(event: CommentEvent):
    print(f"{event.user.nickname} -> {event.comment}")

# Callback registration pattern
client.add_listener("gift", on_gift)
```

All events inherit from `AbstractEvent` with a `name` attribute matching the event type. Events contain `_as_dict` attribute with raw payload.

### Gift Handling (Critical Pattern)
Gifts have **streakable** behavior—type 1 gifts can repeat in streaks:
```python
if event.gift.streakable:
    if not event.gift.streaking:  # Streak ended
        print(f"{event.gift.repeat_count}x {event.gift.extended_gift.name}")
else:  # Non-streakable gift
    print(f"Received {event.gift.extended_gift.name}")
```

### Protobuf Message Parsing
Messages arrive as binary protobuf, deserialized in `proto/utilities.py`:
- `deserialize_message()`: Converts protobuf bytes to dict
- Specific message types (WebcastChatMessage, WebcastGiftMessage, etc.) get additional parsing
- All messages in WebcastResponse have nested `binary` field that gets recursively deserialized

## Client Configuration

### Initialization Options
- `unique_id`: TikTok username (required, auto-normalized with `@`)
- `websocket_enabled=True`: Controls websocket vs polling-only mode
- `process_initial_data=True`: Whether to emit cached events from initial connection
- `enable_extended_gift_info=True`: Fetches gift images/metadata (stored in `available_gifts` dict)
- `sign_api_key`: Optional API key for increased rate limits (contact maintainer)
- `lang="en-US"`: Changes language for extended gift info

### Running the Client
```python
client.run()  # Blocking, starts event loop
await client.start()  # Non-blocking alternative
```

## Custom Utility Library (examples/nandur_lib.py)
Contains project-specific helpers for Indonesian TikTok streams:
- `show_event_picture()`: Downloads & saves profile pics/gift icons
- `save_tiktok_event_to_text_file()`: Persists event data to text files
- `read_username()`: Uses gTTS for text-to-speech in Indonesian (`lang='id'`, `tld='co.id'`)
- `tiktok_id_target()`: Reads target username from `config.ini` (`[TikTok_data]` section)

## Development Notes

### Error Handling
- Websocket errors are logged but don't crash—falls back to polling automatically
- Connection errors raise custom exceptions: `AlreadyConnecting`, `LiveNotFound`, `FailedConnection`
- Register `@client.on("error")` handler to catch runtime errors, otherwise they're logged via `logging.error()`

### Testing Event Handlers
Use `debug=True` when creating client to emit all raw payloads to a `debug` event:
```python
client = TikTokLiveClient("@username", debug=True)
@client.on("debug")
async def on_debug(event):
    print(event.as_dict)  # Raw protobuf data
```

### Examples Directory Structure
- `basic.py`: Minimal setup template
- `gifts.py`: Demonstrates streak handling pattern
- `pygamex.py`: Real-time pygame UI integration
- `nandur_lib.py`: Custom utilities for Indonesian streams
- `DonationSounds/`: Audio playback for donations

## Common Pitfalls
- Don't call protobuf parsing directly—use `from_dict_plus()` from `proto/utilities.py`
- Websocket disconnects set `self.__is_ws_upgrade_done = False` but don't stop polling
- `room_id` only available after successful connection via `client.room_id`
- Event handlers **must be async** when using decorator/listener patterns
- Session IDs expire—handle `InvalidSessionId` exception for long-running connections
