# Git Branching Strategy & Deployment Model

## Overview

This project uses **Git Flow** branching model with semantic versioning for managing releases and features.

```
                     Release Tags
                        ↓
    ┌─────────────────────────────────────────┐
    │         master (v2.1.0, v2.2.0, ...)    │ ← Production releases
    │    Always stable, tagged releases only   │
    └─────────────────────────────────────────┘
                        ↑
                   Merge PR ↑
                        │
    ┌─────────────────────────────────────────┐
    │    develop (main integration branch)     │ ← v2.2.0 features
    │  Collected features ready for release    │
    └─────────────────────────────────────────┘
           ↑           ↑           ↑
           │           │           │
     feature/*    bugfix/*   hotfix/*
     (goal-tracker) (quick-fix) (production-only)
```

---

## Branch Types

### 1. `master` (Production Releases Only)
**Rules**:
- ✅ Merge only from `release` or `hotfix` branches
- ✅ Every commit must be tagged with version (v2.1.0, v2.2.0, etc.)
- ✅ Protected branch: requires PR review before merge
- ✅ Automatic tag creation with release notes
- ❌ Never commit directly to master

**Current state**: v2.1.0 (Stable racing controller)

**Example**:
```bash
# Viewing master history
git log master --oneline --graph

7177ff5 (tag: v2.1.0) release(v2.1.0): Stable Racing Controller
c6a67e2 (tag: v2.0.0) feat(v2.0.0): Initial racing controller
```

---

### 2. `develop` (Integration Branch - Main Development)
**Rules**:
- ✅ Merge feature branches via PR
- ✅ Merge release branches before tagging master
- ✅ Protected branch: requires PR review
- ✅ Must pass CI/tests before merge
- ❌ Never commit directly to develop

**Current state**: Ready for v2.2.0 features

**Purpose**: Collect all features for next version before release

**Feature branches created from develop**:
```
develop
├── feature/goal-tracker           (Goal tracker system)
├── feature/leaderboard            (Donor leaderboard)
├── feature/analytics              (Session analytics)
├── feature/themes                 (Multi-theme overlay)
└── feature/chat-widget            (Comment display)
```

---

### 3. `feature/*` (Feature Development)
**Naming**: `feature/goal-tracker`, `feature/leaderboard`, etc.

**Rules**:
- ✅ Branch from: `develop`
- ✅ Merge back to: `develop` via PR
- ✅ Prefix: `feature/`
- ✅ Scope: Single feature only
- ✅ Lifetime: Delete after merge
- ❌ Never branch from master

**Example workflow**:
```bash
# Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/goal-tracker

# Work on feature
git add goal_tracker.py
git commit -m "feat(goal-tracker): implement goal tracking system"

# Push and create PR
git push origin feature/goal-tracker
# Then open PR on GitHub: develop ← feature/goal-tracker

# After PR merge
git checkout develop
git pull origin develop
git branch -D feature/goal-tracker  # Delete local
git push origin --delete feature/goal-tracker  # Delete remote
```

---

### 4. `bugfix/*` (Non-Critical Bug Fixes)
**Naming**: `bugfix/ipc-timeout`, `bugfix/animation-lag`, etc.

**Rules**:
- ✅ Branch from: `develop`
- ✅ Merge back to: `develop` via PR
- ✅ Prefix: `bugfix/`
- ✅ For bugs found during feature development
- ❌ NOT for production issues (use `hotfix/*`)

**Example**:
```bash
git checkout develop
git checkout -b bugfix/ipc-timeout
# Fix the bug
git commit -m "fix(ipc): reduce timeout from 1.0s to 0.3s"
git push origin bugfix/ipc-timeout
# PR: develop ← bugfix/ipc-timeout
```

---

### 5. `hotfix/*` (Production Hotfixes)
**Naming**: `hotfix/v2.1.1-crash-fix`, etc.

**Rules**:
- ✅ Branch from: `master`
- ✅ Merge to: Both `master` AND `develop`
- ✅ Prefix: `hotfix/`
- ✅ For critical production bugs only
- ✅ Creates minor version bump (v2.1.0 → v2.1.1)
- ❌ Only use for production issues

**Example**:
```bash
# Critical bug in v2.1.0 reported
git checkout master
git checkout -b hotfix/v2.1.1-crash-fix
# Fix critical bug
git commit -m "fix(critical): prevent crash on disconnect"

# Merge to master (with new tag)
git checkout master
git merge --no-ff hotfix/v2.1.1-crash-fix
git tag -a v2.1.1 -m "Hotfix release v2.1.1"

# Merge to develop (keep in sync)
git checkout develop
git merge --no-ff hotfix/v2.1.1-crash-fix

# Delete hotfix branch
git branch -D hotfix/v2.1.1-crash-fix
```

---

## Version Bumping Strategy

### Semantic Versioning: MAJOR.MINOR.PATCH
- **MAJOR** (v3.0.0): Major rewrite or API changes
- **MINOR** (v2.2.0): New features added (monthly releases)
- **PATCH** (v2.1.1): Bug fixes only (as needed)

### Current Versions
```
v2.1.0 (Current - master)  ← Stable racing controller
v2.2.0 (Planned - develop) ← Goal tracker, leaderboard, themes
v2.1.1 (Potential hotfix)  ← Production bugs only
v3.0.0 (Future)            ← Major rewrite
```

---

## Release Process

### Creating v2.2.0 Release (Example)

#### Step 1: Prepare Release
```bash
# On develop: collect all v2.2.0 features
git checkout develop
git pull origin develop

# Verify all feature branches are merged
git log --oneline develop | head -20

# Update version numbers
# - racing_app/config.json: version = "2.2.0"
# - .github/copilot-instructions.md: Update to v2.2.0
# - Create RELEASE_NOTES_v2.2.0.md

git add racing_app/config.json .github/copilot-instructions.md RELEASE_NOTES_v2.2.0.md
git commit -m "chore(release): prepare v2.2.0"
git push origin develop
```

#### Step 2: Create Release Branch (Optional but Recommended)
```bash
# For larger releases, create release branch
git checkout -b release/v2.2.0

# Final testing and version bumps
# Then merge to master
git checkout master
git merge --no-ff release/v2.2.0
git tag -a v2.2.0 -m "Release v2.2.0: Goal tracker, leaderboard, themes"
git push origin master --tags

# Merge back to develop
git checkout develop
git merge --no-ff release/v2.2.0
git push origin develop

# Delete release branch
git branch -D release/v2.2.0
```

#### Step 3: Deploy
```bash
git checkout v2.2.0
# Run tests, etc.
# Then merge to any deployment branches if needed
```

---

## Current Project Structure (v2.1.0)

```
master ─────────────────────────────→ tag: v2.1.0 (Current)
           ↑
           │ (PR merge from develop)
           │
develop ───┴─────────────────────────→ Ready for v2.2.0

v2.2.0 Branches (active):
├── feature/goal-tracker          (2-3 hours)
├── feature/leaderboard           (2 hours)
├── feature/analytics             (6 hours)
├── feature/themes                (2 hours)
└── feature/chat-widget           (3 hours)

Planned merge order:
1. goal-tracker → develop
2. leaderboard → develop
3. analytics → develop
4. themes → develop
5. chat-widget → develop
6. develop → master (tag v2.2.0)
```

---

## Commit Message Format

### Standard Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **chore**: Maintenance, version bump
- **docs**: Documentation only
- **refactor**: Code restructuring
- **perf**: Performance improvement
- **test**: Test additions
- **ci**: CI/CD changes
- **release**: Release commit

### Scope
- `goal-tracker`: Goal tracking feature
- `leaderboard`: Leaderboard system
- `analytics`: Analytics dashboard
- `themes`: Overlay themes
- `ipc`: IPC communication
- `overlay`: Electron overlay
- etc.

### Examples
```
feat(goal-tracker): implement goal tracking system
↑    ↑              ↑
type scope         subject

fix(ipc): reduce timeout to prevent UI hang

chore(release): prepare v2.2.0 for release

docs(README): add branching strategy guide
```

---

## Common Workflows

### Starting a New Feature
```bash
# Make sure develop is up to date
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/my-feature

# Work and commit with proper messages
git add file.py
git commit -m "feat(my-feature): add new capability"

# Push regularly
git push origin feature/my-feature

# When ready, open PR on GitHub
```

### Syncing Feature with Develop
```bash
# If develop has new commits
git checkout feature/my-feature
git fetch origin
git merge origin/develop
# Resolve conflicts if any
git push origin feature/my-feature
```

### Updating Master After Release
```bash
# Master is ahead, bring develop up to date
git checkout develop
git pull origin develop
git merge origin/master
git push origin develop
```

---

## Branch Protection Rules (Recommended)

### For `master`:
- ✅ Require pull request review (1 approver minimum)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date before merge
- ✅ Require signed commits
- ✅ Allow force pushes: NO
- ✅ Allow deletions: NO

### For `develop`:
- ✅ Require pull request review (1 approver minimum)
- ✅ Require status checks to pass
- ✅ Allow force pushes: NO
- ✅ Allow deletions: NO

### For `feature/*`, `bugfix/*`:
- ✅ None (developers control)

---

## GitHub Release Management

### Automatic Release Notes
```bash
# Tag v2.2.0 on master
git tag -a v2.2.0 -m "Release v2.2.0: Goal tracker, leaderboard, themes"

# GitHub automatically creates release with:
# - Tag name: v2.2.0
# - Title: Release v2.2.0
# - Description: (from -m flag)
# - Auto-generated changelog from PRs merged
```

### Manual Release Notes
On GitHub:
1. Go to Releases → Create release
2. Select tag: v2.2.0
3. Title: "Release v2.2.0"
4. Description: Full release notes (copy from RELEASE_NOTES.md)
5. Mark as "Latest release"

---

## Troubleshooting

### Accidentally pushed to master
```bash
# Don't panic! Use git revert
git checkout master
git revert HEAD  # Creates undo commit
git push origin master
```

### Wrong branch for feature
```bash
# If you branched from master instead of develop
git rebase develop
# Or merge develop into your feature
git merge develop
```

### Merge conflicts during PR
```bash
# Pull latest develop
git fetch origin
git merge origin/develop
# Resolve conflicts in your editor
git add resolved-files.py
git commit -m "resolve merge conflicts"
git push origin feature/my-feature
```

---

## Summary

| Branch | From | To | When | Lifetime |
|--------|------|-----|------|----------|
| `master` | - | - | Production releases | Permanent |
| `develop` | - | - | Integration | Permanent |
| `feature/*` | develop | develop | New features | Temporary (delete after merge) |
| `bugfix/*` | develop | develop | Bug fixes | Temporary |
| `hotfix/*` | master | master + develop | Production fixes | Temporary |
| `release/*` | develop | master | Release prep | Temporary (optional) |

**Current Status**:
- ✅ `master` at v2.1.0 (stable)
- ✅ `develop` ready for v2.2.0 (feature branches created)
- ✅ Git Flow properly configured
- ✅ Ready for feature development cycle

---

**Last updated**: 2026-02-03  
**Maintained by**: @nandurstudio
