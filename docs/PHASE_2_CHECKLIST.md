# Phase 2 Implementation Checklist

**Status**: Ready to Start  
**Priority**: 2.1 (Comment Avatars) → 2.2 (Likes) → 2.3 (Gifts) → 2.4 (Dashboard)  
**Est. Time**: ~8 hours total

---

## Feature 2.1: Comment Author Profile Pictures [HIGH PRIORITY]
**Est. Time**: 2-3 hours  
**Complexity**: Medium

### Tasks
- [ ] Create `cache/avatars/` directory on startup
- [ ] Implement `_download_avatar(user_id, avatar_url)` method
  - [ ] Use aiohttp for async HTTP requests
  - [ ] Save to `cache/avatars/{user_id}.jpg`
  - [ ] Implement retry logic for failed downloads
  - [ ] Cache for 24 hours (check timestamp)
- [ ] Modify `_handle_comment()` to fetch avatars
  - [ ] Extract avatar URL from `event.user.avatar`
  - [ ] Call download async method
  - [ ] Don't block event processing (async)
- [ ] Update console output format
  - [ ] Show avatar path with comment
  - [ ] Format: `[AVATAR] path/to/avatar.jpg` then `[COMMENT] @user -> "message"`
- [ ] Error handling
  - [ ] Graceful fallback if download fails
  - [ ] Log at DEBUG level (not blocking)
  - [ ] Continue processing even if avatar missing
- [ ] Configuration option
  - [ ] Add to config.json: `"enable_profile_pictures": true`
  - [ ] Make feature toggleable

### Success Criteria
- [ ] Avatars downloaded and cached locally
- [ ] No performance impact (async download)
- [ ] Displayed with each comment in output
- [ ] Handles missing/invalid images gracefully
- [ ] Works with real TikTok stream

### Testing
```bash
python launcher.py
# Select: Real → Production
# Watch comments - should show "[AVATAR] cache/avatars/user_id.jpg"
# Check cache/ folder for downloaded images
```

---

## Feature 2.2: Liker Information Display [MEDIUM PRIORITY]
**Est. Time**: 1-2 hours  
**Complexity**: Low

### Tasks
- [ ] Add LikeEvent handler
  - [ ] Register: `@client.on(LikeEvent)`
  - [ ] Method: `_handle_like(event: LikeEvent)`
- [ ] Track unique likers
  - [ ] Use `set()` for unique user IDs
  - [ ] Use `deque(maxlen=5)` for recent likers
  - [ ] Store: `(username, timestamp)`
- [ ] Real-time like display
  - [ ] Print immediately: `[LIKE] @username`
  - [ ] Update total: `[LIKE COUNTER] X likes (Rate: Y/min)`
- [ ] Calculate like rate
  - [ ] Track likes per minute
  - [ ] Update every 10 seconds
- [ ] Periodic summary (every 30s)
  - [ ] Show recent 5 likers
  - [ ] Show total like count
  - [ ] Show like rate for period
- [ ] Integration with engagement metrics
  - [ ] Add to `self.engagement_metrics['likes']`
  - [ ] Update leaderboard tracking

### Success Criteria
- [ ] LikeEvent detected and processed
- [ ] Unique likers tracked correctly
- [ ] Real-time counter displayed
- [ ] Like rate calculated accurately
- [ ] Periodic summaries show correct data
- [ ] No duplicate counting in short windows

### Testing
```bash
python launcher.py
# In mock mode, viewers will generate random likes
# Or test with real stream for organic likes
# Should see: [LIKE] @username with counter updates
```

---

## Feature 2.3: Gift Donor Recognition [MEDIUM PRIORITY]
**Est. Time**: 3-4 hours  
**Complexity**: Medium

### Tasks
- [ ] Add GiftEvent handler
  - [ ] Register: `@client.on(GiftEvent)`
  - [ ] Method: `_handle_gift(event: GiftEvent)`
- [ ] Extract gift information
  - [ ] `event.user.nickname` → donor name
  - [ ] `event.gift.extended_gift.name` → gift name
  - [ ] `event.gift.repeat_count` → count
  - [ ] `event.gift.extended_gift.diamond_count` → diamonds per gift
- [ ] **CRITICAL: Streak handling**
  - [ ] Check `event.gift.streakable` (type 1 = streakable)
  - [ ] For streakable: Check `event.gift.streaking`
  - [ ] Only announce when `not streaking` (streak ended)
  - [ ] Announce with total: `{count}x {gift_name} ({total_diamonds})`
  - [ ] For non-streakable: Announce immediately
- [ ] Track gift information
  - [ ] Store in `GiftInfo` dataclass:
    ```python
    @dataclass
    class GiftInfo:
        name: str
        count: int
        diamonds: int
        donor: str
        timestamp: datetime
    ```
- [ ] Display notifications
  - [ ] Format: `[GIFT] @username -> {count}x {gift_name} ({diamonds} diamonds)`
  - [ ] Print to console/log on announcement
- [ ] Top donor tracking
  - [ ] Maintain dict: `{donor_name: total_diamonds}`
  - [ ] Update on each gift announcement
  - [ ] Display top 5-10 every 2 minutes:
    ```
    [TOP DONORS]
    1. @user1: 500 diamonds
    2. @user2: 300 diamonds
    ...
    ```
- [ ] Extended gift info
  - [ ] Download gift icons (similar to avatars)
  - [ ] Cache in `cache/gifts/{gift_name}.jpg`
  - [ ] Display with gift notification

### Success Criteria
- [ ] GiftEvent properly parsed
- [ ] Streak handling 100% correct (no double-announces)
- [ ] Diamond values calculated correctly
- [ ] Top donors tracked and displayed
- [ ] Gift notifications appear at right time
- [ ] Gift icons cached and displayed

### Critical Pattern (DO NOT CHANGE)
```python
if event.gift.streakable:
    if not event.gift.streaking:  # Streak ENDED
        # ANNOUNCE HERE with repeat_count
        count = event.gift.repeat_count
        print(f"{count}x {gift_name}")
    # Don't announce during streak (streaking=True)
else:  # Non-streakable
    # ANNOUNCE IMMEDIATELY
    print(f"{gift_name}")
```

### Testing
```bash
python launcher.py
# Use mock mode - will simulate gifts with streaks
# OR test with real stream
# Should see:
#   - No announces during streaks
#   - Announce when streak ends with total count
#   - Non-streakable gifts announce immediately
```

---

## Feature 2.4: Engagement Dashboard [LOW PRIORITY]
**Est. Time**: 1-2 hours  
**Complexity**: Low

### Tasks
- [ ] Create engagement metrics aggregation
  - [ ] Consolidate comments, likes, gifts data
  - [ ] Calculate summary statistics
  - [ ] Track time windows (last 30s)
- [ ] Implement periodic display (every 30s)
  - [ ] Collect metrics for period
  - [ ] Format output:
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
  - [ ] Display to console
  - [ ] Log to DEBUG level
- [ ] Reset counters between summaries
  - [ ] Clear temporary data after display
  - [ ] Keep cumulative totals
- [ ] Integration with other features
  - [ ] Pull data from engagement_metrics dict
  - [ ] Combine comments, likes, gifts info
  - [ ] Calculate rates and rankings

### Success Criteria
- [ ] Metrics collected correctly
- [ ] Summary displays every 30 seconds
- [ ] All calculations accurate
- [ ] Counters reset between displays
- [ ] Output format clean and readable

### Testing
```bash
python launcher.py
# Run in mock mode (generates simulated data)
# After 30 seconds, should see summary
# Check console for: Comments, Likes, Gifts, Top Donor, Most Active
```

---

## Installation & Setup

### Install Dependencies
```bash
pip install Pillow aiohttp
```

### Create Cache Directories
```bash
mkdir cache/avatars cache/gifts
```

### Update requirements.txt
```
Pillow>=10.0.0
aiohttp>=3.8.0
```

---

## Code Location & Patterns

### Where to Add Code
- **Main controller**: `examples/racing_game_controller.py`
- **New methods**: Add to `RacingGameController` class
- **Event handlers**: Register with `@client.on(EventType)`
- **Config**: Add new options to `config.json` structure

### Existing Patterns to Follow
```python
# Existing event handler pattern
@self.client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    await self._handle_comment(event)

# Async pattern for downloads
async def _download_avatar(self, user_id: str, url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.read()

# Storage pattern
self.engagement_metrics = {
    'comments': [],
    'likes': [],
    'gifts': [],
}
```

### Data Access Examples
```python
# From CommentEvent
username = event.user.nickname
user_id = event.user.unique_id
avatar_url = event.user.avatar[0]  # First avatar URL
comment = event.comment

# From LikeEvent
username = event.user.nickname
user_id = event.user.unique_id

# From GiftEvent
username = event.user.nickname
gift_name = event.gift.extended_gift.name
gift_count = event.gift.repeat_count
is_streakable = event.gift.streakable
is_streaking = event.gift.streaking
diamond_value = event.gift.extended_gift.diamond_count
```

---

## Testing Checklist

### Per Feature Testing
- [ ] 2.1: Avatar downloads and caches properly
- [ ] 2.1: No lag from async downloads
- [ ] 2.1: Handles missing/invalid images
- [ ] 2.2: Like events detected
- [ ] 2.2: Like rate calculated correctly
- [ ] 2.2: Unique likers tracked (no duplicates in 5s)
- [ ] 2.3: Streak handling correct (no double-announce)
- [ ] 2.3: Diamond values accurate
- [ ] 2.3: Top donor list maintains correctly
- [ ] 2.4: Summary displays every 30s
- [ ] 2.4: All metrics accurate in dashboard

### Integration Testing
- [ ] All features work together
- [ ] No conflicts between handlers
- [ ] Console output clean and readable
- [ ] Performance acceptable (< 5% CPU increase)
- [ ] Logging at appropriate levels

### Real TikTok Testing
- [ ] Test with actual live stream
- [ ] Verify avatars download
- [ ] Verify likes tracked from real viewers
- [ ] Verify gifts recognized
- [ ] Verify dashboard displays

---

## Quality Checklist

Before marking complete:
- [ ] Code follows existing patterns
- [ ] Async operations properly await
- [ ] Error handling graceful (logging, fallbacks)
- [ ] No blocking operations in event loop
- [ ] Unicode/UTF-8 safe (Windows compatible)
- [ ] Performance acceptable
- [ ] Logging at DEBUG level available
- [ ] Documentation updated

---

## Estimated Timeline

```
Phase 2 Development:
  Week 1:
    - Mon: 2.1 Profile avatars (4-6 hrs)
    - Tue: 2.1 Testing & fixes (2-3 hrs)
    - Wed: 2.2 Like tracking (2-3 hrs)
    - Thu: 2.2 Testing, 2.3 start (3-4 hrs)
    - Fri: 2.3 Gift recognition (4-5 hrs)
  
  Week 2:
    - Mon: 2.3 Testing & fixes (2-3 hrs)
    - Tue: 2.3 Streak handling verification (2-3 hrs)
    - Wed: 2.4 Dashboard implementation (2-3 hrs)
    - Thu: 2.4 Testing, integration (2-3 hrs)
    - Fri: Final testing, documentation (2-3 hrs)

Total: ~8-10 hours development
       ~6-8 hours testing
       ~3-4 hours documentation
       = ~17-22 hours Phase 2 total
```

---

## Success Criteria - Phase 2 Complete

- [ ] Profile pictures extracted from comments
- [ ] Avatars downloaded and cached
- [ ] Like counter shows real-time updates
- [ ] Likes tracked per unique user
- [ ] Gift notifications announce on streak end
- [ ] Non-streakable gifts announce immediately
- [ ] Top donor list accurate and updating
- [ ] Engagement dashboard displays summary
- [ ] All features tested with real TikTok
- [ ] Performance unchanged or improved
- [ ] Documentation updated with examples
- [ ] Code quality maintained

---

## Getting Started

1. **Review Phase 2 Plan**: Read [ROADMAP.md](../ROADMAP.md)
2. **Review Existing Code**: Study `racing_game_controller.py` patterns
3. **Start 2.1**: Implement profile picture downloads
4. **Test Continuously**: After each feature, test with real stream
5. **Iterate**: Improve based on testing feedback
6. **Document**: Update guides as you build

---

**Ready to build Phase 2! 🚀**

See you in the code!
