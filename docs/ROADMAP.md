# TikTok Live Racing Controller - Development Roadmap

## Summary
Production-ready TikTok LIVE controller for real-time racing games with multi-game support. Phase 1 complete. Phase 2 ready for implementation.

---

## Phase 1: ✅ COMPLETE - Core Racing Controller
**Status**: COMPLETED  
**Duration**: ~2 weeks  
**Codebase Status**: Clean, organized, production-ready (50% smaller after cleansing)

### Achievements
- [x] TikTok LIVE connection & event listening (WebSocket + polling)
- [x] Keyboard command mapping (25+ single + 4 combo keys)
- [x] Per-user cooldown & anti-spam system (0.2s default, 0.1-0.5s configurable)
- [x] Debug mode (safe testing without keyboard input)
- [x] Movement key hold functionality (W/A/S/D held 5s, configurable)
- [x] Combination keys (WS, WD, AS, SD for complex moves)
- [x] Multi-game configuration (NFS HEAT, GTA V, MINECRAFT)
- [x] Interactive setup & configuration management (config.json)
- [x] Pre-flight validation (username & stream check)
- [x] Comprehensive logging & statistics tracking
- [x] UTF-8 encoding (Windows PowerShell compatible)
- [x] Unified launcher (Real/Mock × Debug/Prod)
- [x] Codebase cleansing (removed 50+ redundant files)

### Current Capabilities
```
Games Supported: 3 (NFS HEAT, GTA V, MINECRAFT)
Command Mappings: 25+ single + 4 combo per game
Multi-Language: English + Indonesian commands
Anti-Spam: Per-user cooldown (0.1-0.5s configurable)
Testing Modes: Real TikTok + Mock with simulated viewers
Repository Size: 50% reduction (100+ → ~60 files)
```

### Key Features
✅ Event-driven architecture with async/await  
✅ Unified config.json for multiple games  
✅ Game selection at startup  
✅ Per-game custom command mappings  
✅ Real-time command processing from TikTok chat  
✅ Professional, clean codebase
✅ Comprehensive documentation (8 markdown guides)  

---

## Phase 2: 🚀 NEXT - Viewer Engagement Display
**Status**: Ready for Implementation  
**Est. Duration**: 1-2 weeks  
**Dependencies**: Pillow, aiohttp

### Objectives
Display real-time viewer information for engagement tracking and recognition

---

### Priority 2.1: Comment Author Profile Picture [HIGH]
**Goal**: Display profile pictures of commenters for visual feedback

**Tasks**:
1. Extract `user.avatar` URL from `CommentEvent`
   - Access: `event.user.avatar` (list of avatar URLs)
   - Fallback: Use placeholder if unavailable
   
2. Async image downloading with caching
   - Cache directory: `cache/avatars/`
   - Filename: `{user_id}.jpg`
   - TTL: 24 hours (refresh daily)
   - Prevent duplicate downloads
   
3. Display integration
   - Show thumbnail (100x100px) when comment received
   - Console output format:
     ```
     [AVATAR] cached/avatars/user_id.jpg
     [COMMENT] @username -> "w"
     ```
   
4. Error handling
   - Graceful fallback if download fails
   - Log failures at DEBUG level
   - Don't block main event processing

**Dependencies**: `Pillow`, `aiohttp`  
**Estimated Time**: 2-3 hours  
**Success Criteria**:
- [ ] Profile pictures downloaded and cached
- [ ] Displayed with each comment in real-time
- [ ] No performance degradation
- [ ] Graceful error handling

---

### Priority 2.2: Liker Information Display [MEDIUM]
**Goal**: Track and display viewers who like the stream

**Tasks**:
1. Listen for `LikeEvent` from TikTok
   - Track unique user IDs
   - Store liker nicknames with timestamp
   - Calculate like rate (likes/minute)
   
2. Deduplication logic
   - Don't count same user twice in 5s window
   - Update count if same user likes again
   
3. Real-time display
   - Show new likers immediately:
     ```
     [LIKE] @username
     ```
   - Update counter every 10s with rate:
     ```
     [LIKE COUNTER] 24 likes (Rate: 2.4/min)
     ```
   
4. Periodic summary (every 30s)
   - Show last 5 unique likers
   - Show total like rate for session
   
5. Statistics integration
   - Add to `engagement_metrics` dict
   - Track peak like times

**Dependencies**: None (SDK built-in)  
**Estimated Time**: 1-2 hours  
**Success Criteria**:
- [ ] LikeEvent properly parsed
- [ ] Unique liker detection working
- [ ] Real-time like rate calculated
- [ ] Periodic summaries displayed
- [ ] No false positives

---

### Priority 2.3: Gift Donor Recognition [MEDIUM]
**Goal**: Track and celebrate gift donations with detailed info

**Critical Pattern** (from existing codebase):
```python
# NEVER announce during streak, only when streak ENDS
if event.gift.streakable:
    if not event.gift.streaking:  # Streak ended!
        print(f"{count}x {event.gift.extended_gift.name}")
else:  # Non-streakable
    print(f"{event.gift.extended_gift.name}")
```

**Tasks**:
1. Listen for `GiftEvent`
   - Extract: gift name, count, type (streakable/not)
   - Get donor: `event.user.nickname`
   - Calculate: diamonds per gift
   
2. Gift streak handling (CRITICAL)
   - Streakable gifts: Wait for streak to end
   - Don't announce during streak (check `event.gift.streaking`)
   - Announce at end with total count
   - Non-streakable: Announce immediately
   
3. Gift value calculation
   - Diamond cost mapping per gift name
   - Total value = cost × count
   - Track cumulative stream total
   
4. Real-time notifications
   - Announce when streak ends:
     ```
     [GIFT] @username -> 5x Gold Egg (150 diamonds)
     ```
   - Non-streakable gifts:
     ```
     [GIFT] @username -> Diamond Ring (300 diamonds)
     ```
   
5. Top donor tracking
   - Maintain leaderboard (top 5-10)
   - Sort by: total diamonds sent
   - Display every 2 minutes:
     ```
     [TOP DONORS]
     1. @user1: 500 diamonds
     2. @user2: 300 diamonds
     ```
   
6. Extended gift info
   - Display gift type/rarity
   - Download and cache gift icons
   - Show alongside gift name

**Data Structure**:
```python
@dataclass
class GiftInfo:
    name: str
    count: int
    diamonds: int
    donor: str
    timestamp: datetime
```

**Dependencies**: None (pattern already in controller)  
**Estimated Time**: 3-4 hours  
**Success Criteria**:
- [ ] GiftEvent properly parsed
- [ ] Streak handling implemented correctly
- [ ] No duplicate announcements during streaks
- [ ] Diamond values calculated accurately
- [ ] Top donor list maintains correctly
- [ ] Gift icons cached and displayed

---

### Priority 2.4: Engagement Dashboard [LOW]
**Goal**: Unified summary of all viewer interactions

**Task**: Display every 30s:
```
==================================================
ENGAGEMENT SUMMARY (Last 30 seconds)
==================================================
Comments:     12 from 8 unique users
Likes:        45 people (Rate: 1.5/min)
Gifts:        3 donors x 420 diamonds
Top Donor:    @user1 (150 diamonds)
Most Active:  @user2 (4 commands)
==================================================
```

**Dependencies**: Phases 2.1-2.3  
**Estimated Time**: 1-2 hours  
**Success Criteria**:
- [ ] Metrics collected correctly
- [ ] Counters reset between summaries
- [ ] Accurate calculations
- [ ] Clean display format

---

## Phase 3: 💻 UI/Visualization (Optional - Future)
**Status**: Not Started  
**Est. Duration**: 2-3 weeks

### Possible Features
- [ ] ASCII art dashboard (console-based)
- [ ] Pygame overlay on game screen
- [ ] Web UI (Flask/FastAPI) for streaming dashboard
- [ ] Real-time viewer list with avatars
- [ ] Command history visualization
- [ ] Statistics charts

---

## Implementation Timeline - Phase 2

| Feature | Complexity | Time | Status |
|---------|-----------|------|--------|
| 2.1 Profile Avatars | Medium | 2-3h | [  ] Not Started |
| 2.2 Like Tracking | Low | 1-2h | [  ] Not Started |
| 2.3 Gift Recognition | Medium | 3-4h | [  ] Not Started |
| 2.4 Engagement Dashboard | Low | 1-2h | [  ] Not Started |
| **Phase 2 Total** | | **~8 hours** | |

---

## Installation - Phase 2 Setup

### Step 1: Install Dependencies
```bash
pip install Pillow aiohttp
```

### Step 2: Update requirements.txt
```
Pillow>=10.0.0
aiohttp>=3.8.0
```

### Step 3: Create Cache Directory
```bash
mkdir cache/avatars cache/gifts
```

---

## Code Architecture - Phase 2

### New Methods in RacingGameController

```python
# Avatar management (2.1)
async def _download_avatar(self, user_id: str, avatar_url: str) -> str:
    """Download and cache profile picture"""
    
async def _cache_avatar(self, user_id: str, image_bytes: bytes) -> str:
    """Save image to cache"""

# Gift handling (2.3 - enhance existing)
async def _handle_gift(self, event: GiftEvent):
    """Process gift event with streak detection"""

# Like handling (2.2)
async def _handle_like(self, event: LikeEvent):
    """Process like event"""

# Engagement tracking (2.4)
def _update_engagement_metrics(self, event_type: str, event: AbstractEvent):
    """Update engagement counters"""
    
def _display_engagement_summary(self):
    """Show periodic engagement summary"""

# Utilities
def _calculate_gift_value(self, gift_name: str, count: int) -> int:
    """Calculate diamond value"""
    
def _format_engagement_output(self) -> str:
    """Format dashboard output"""
```

### Data Structures
```python
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime

@dataclass
class GiftInfo:
    name: str
    count: int
    diamonds: int
    donor: str
    timestamp: datetime

@dataclass
class LikeInfo:
    user: str
    timestamp: datetime

# In __init__:
self.engagement_metrics = {
    'comments': [],
    'likes': [],
    'gifts': [],
    'top_donors': {},
    'session_start': datetime.now(),
    'avatar_cache': {},
}
```

---

## Testing Strategy - Phase 2

### Test Environment
```python
# Use mock mode for rapid iteration
python launcher.py
# Select: Mock mode → Real TikTok later for validation
```

### Test Cases per Feature

**2.1 Profile Avatars**:
- [ ] Avatar URL extracted correctly
- [ ] Image downloaded without blocking
- [ ] Image cached to local directory
- [ ] Graceful handling if URL invalid
- [ ] Display works with cached image

**2.2 Like Tracking**:
- [ ] Like events detected
- [ ] Unique users tracked
- [ ] Like rate calculated
- [ ] Summary displays every 30s
- [ ] Counter updates in real-time

**2.3 Gift Recognition**:
- [ ] Gift events detected
- [ ] Streak handling works (no double-announce)
- [ ] Diamond values correct
- [ ] Top donor list accurate
- [ ] Notifications formatted properly

**2.4 Dashboard**:
- [ ] All metrics collected
- [ ] Summary formatted correctly
- [ ] Displays every 30s
- [ ] No performance impact

---

## Quality Checklist - Phase 2

Before marking features complete:
- [ ] Tested with real TikTok stream (not just mock)
- [ ] No performance degradation (< 5% CPU increase)
- [ ] Graceful error handling (network failures don't crash)
- [ ] Logging available (DEBUG level for troubleshooting)
- [ ] Code follows existing patterns
- [ ] Documentation updated with examples

---

## Documentation Updates - Phase 2

After implementation, create/update:
- [ ] PHASE_2_IMPLEMENTATION.md (code examples)
- [ ] ENGAGEMENT_DISPLAY.md (feature guide)
- [ ] TROUBLESHOOTING.md (common issues)
- [ ] Update COMMANDS_REFERENCE.md with new event types
- [ ] Update README.md with new features

---

## Rollback Plan

If Phase 2 implementation causes issues:
1. Git revert to last known good state
2. Run `git log --oneline` to find stable commit
3. Disable problematic feature in config.json
4. Document issue in GitHub Issues

---

## Success Metrics - Phase 2 Complete

- [ ] Profile pictures display with each comment
- [ ] Like counter shows real-time updates
- [ ] Gift notifications announce when streak ends
- [ ] Top donor list updates correctly
- [ ] Engagement dashboard displays periodic summary
- [ ] Zero false positives or duplicate announcements
- [ ] Performance unchanged from Phase 1
- [ ] All documentation updated

---

## Next Steps

1. **Review Roadmap**: Confirm priorities and timeline
2. **Setup Environment**: Install dependencies, create cache dirs
3. **Start 2.1**: Implement profile avatar downloads
4. **Test Continuously**: Real TikTok stream testing after each feature
5. **Iterate**: Improve based on testing feedback
6. **Document**: Keep docs updated throughout

---

**Roadmap Last Updated**: After Phase 1 completion + codebase cleansing  
**Status**: Phase 2 ready for development start  
**Next Milestone**: Phase 2 implementation kicks off

---

## Documentation Plan - Phase 2

### New Guides to Create
- [ ] `VIEWER_DISPLAY_GUIDE.md` - How to enable viewer features
- [ ] `ENGAGEMENT_TRACKING.md` - Understanding metrics
- [ ] `IMAGE_CACHING.md` - Profile picture management

### Updates to Existing Docs
- [ ] Update `MULTI_GAME_CONFIG.md` with display settings
- [ ] Update `COMMANDS_REFERENCE.md` with new events
- [ ] Update main `README.md` with new features

---

## Testing Plan - Phase 2

### Test Cases
```python
# test_phase2_features.py

def test_extract_profile_picture_url():
    """Verify profile picture extraction from event"""

def test_download_and_cache_image():
    """Test image download and local caching"""

def test_like_event_tracking():
    """Track unique likers and display"""

def test_gift_event_parsing():
    """Extract gift info and format display"""

def test_periodic_summary_display():
    """Verify periodic liker/gift summaries"""
```

---

## Dependencies

### New Libraries Needed
- `Pillow` (PIL) - Image handling
- `aiofiles` - Async file operations
- `requests` (if async) or `aiohttp` - Image downloading

### Installation
```bash
pip install Pillow aiohttp
```

---

## Success Metrics - Phase 2

✅ Viewers can see who is engaging (commenters, likers, gifters)  
✅ Profile pictures shown for comments  
✅ Liker recognition with periodic updates  
✅ Gift donations clearly displayed  
✅ Top donors / gifters highlighted  
✅ Real-time engagement dashboard  
✅ Zero performance impact on main controller  

---

## Timeline

| Phase | Status | Start | End | Duration |
|-------|--------|-------|-----|----------|
| Phase 1: Core Controller | ✅ Complete | Week 1 | Week 2 | 2 weeks |
| Phase 2: Viewer Display | 🚀 Next | Week 3 | Week 4 | 1-2 weeks |
| Phase 3: UI/Dashboard | 📅 Future | TBD | TBD | 2-3 weeks |

---

## Priority Ranking - Phase 2

1. **HIGH**: Profile picture display + Liker names
2. **MEDIUM**: Gift donor recognition
3. **MEDIUM**: Engagement dashboard
4. **LOW**: Advanced metrics/statistics

---

## Notes

- Profile pictures can be cached locally to reduce bandwidth
- Liker/gift information should not impact command processing performance
- Use async operations to prevent blocking
- Consider rate limiting for frequent displays
- Optional: Store engagement data to file for later analysis

---

## Next Steps

1. ✅ Cleanse codebase (DONE)
2. 📋 Review Phase 2 requirements
3. 🔄 Implement profile picture extraction & display
4. 🔄 Implement liker tracking & display
5. 🔄 Implement gift donor recognition
6. ✅ Create documentation
7. ✅ Write tests
8. ✅ Code review & deployment

---

**Last Updated**: 2026-02-02  
**Next Review**: After Phase 2 Implementation
