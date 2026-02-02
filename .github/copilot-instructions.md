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

## AI Agent Behavior Guidelines

### ⚠️ CRITICAL - DO NOT:
1. **Never perform destructive operations** on crucial/core files without explicit user approval
   - Don't delete core library files
   - Don't modify critical configs without asking
   - Don't break existing functionality

2. **Never hardcode credentials, API keys, or secrets**
   - ALWAYS store sensitive data in `.env` file
   - Use `python-dotenv` to load environment variables
   - Never commit secrets to git
   - Never log sensitive information

3. **Never spam markdown/documentation files**
   - Only create/modify docs when explicitly requested
   - Don't auto-generate documentation without permission
   - Consolidate updates into single files when possible

4. **Never commit or push to git automatically**
   - Always wait for explicit `git add`, `commit`, or `push` request
   - Ask for confirmation before pushing
   - Inform user of pending changes that need manual commit

### ✅ BEST PRACTICES:
- Ask for confirmation before making breaking changes
- Always suggest alternatives before deletion
- Keep sensitive data in `.env` (add to `.gitignore`)
- Report what would change before doing it
- Wait for explicit user permission for git operations
### ⚠️ TERMINAL SYNTAX - POWERSHELL ONLY

**ALWAYS use PowerShell syntax. User is on Windows with PowerShell.**

#### ❌ WRONG - Never use Bash/Unix syntax:
```powershell
# DON'T DO THIS:
echo "text" | command          # Unix pipe
command1 && command2           # Unix AND
command1; command2             # Unix semicolon chaining (wrong context)
head -20                        # Unix command
cat file.txt                    # Unix command
export VAR=value              # Unix export
timeout 5 command              # Windows timeout command syntax is different
```

#### ✅ CORRECT - Use PowerShell syntax:
```powershell
# DO THIS INSTEAD:
Write-Output "text" | command                    # PowerShell pipe (same as Bash)
command1 ; command2                              # PowerShell semicolon (correct!)
Select-Object -First 20                          # PowerShell equivalent of head
Get-Content file.txt                             # PowerShell equivalent of cat
$env:VAR = "value"                              # PowerShell environment variable
Start-Sleep -Seconds 5; command                  # PowerShell sleep + command

# More examples:
ls → Get-ChildItem
cd → Set-Location or Push-Location/Pop-Location
mkdir → New-Item -ItemType Directory
cp → Copy-Item
mv → Move-Item
rm → Remove-Item
grep → Select-String
```

#### 📋 COMMON MISTAKES TO AVOID:

1. **Piping to `head`** ❌
   ```powershell
   # WRONG:
   python script.py 2>&1 | head -20
   
   # CORRECT:
   python script.py 2>&1 | Select-Object -First 20
   ```

2. **Using `&&` for chaining** ❌
   ```powershell
   # WRONG:
   python script.py && echo "Done"
   
   # CORRECT:
   python script.py ; echo "Done"
   # OR
   python script.py; Write-Output "Done"
   ```

3. **Using `echo` instead of `Write-Output`** ❌
   ```powershell
   # WRONG (echo exists but works differently):
   echo "test" > file.txt
   
   # CORRECT:
   "test" | Out-File file.txt
   # OR for simple write:
   Write-Output "test"
   ```

4. **Using `timeout` incorrectly** ❌
   ```powershell
   # WRONG:
   timeout 5 python script.py
   
   # CORRECT:
   Start-Process python -ArgumentList "script.py" -Wait
   # Or use Job-based approach for more control
   ```

5. **Using `<` for input redirection** ❌
   ```powershell
   # WRONG (not supported):
   python script.py < input.txt
   
   # CORRECT:
   Get-Content input.txt | python script.py
   ```

#### 🎯 TERMINAL COMMAND BEST PRACTICES:

When running terminal commands:
1. **Always check if command exists in PowerShell first**
2. **Use `Get-*` cmdlets for retrieval** (Get-ChildItem, Get-Content, etc.)
3. **Use pipes `|` correctly** (PowerShell pipes work like Bash)
4. **Use semicolons `;` for command chaining**
5. **Use `Write-Output` or `-` for output** (not `echo`)
6. **Avoid external tools** unless PowerShell equivalent doesn't exist

#### 📌 SAFE POWERSHELL PATTERNS:

```powershell
# List files
Get-Item path\to\files | Select-Object Name, Length, LastWriteTime

# Get first/last N lines
command-output | Select-Object -First 20
command-output | Select-Object -Last 10

# Filter output
command-output | Where-Object {$_.Length -gt 1000}

# Format table
command-output | Format-Table -AutoSize

# Combine operations
Get-ChildItem | Where-Object {$_.Extension -eq ".py"} | Select-Object Name
```