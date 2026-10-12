# Rescue Runner — test report (Loop 7)

**File:** `Rescue_Runner.sb3` (976 KB) — Stage + exactly 4 sprites, 485 blocks in 29 scripts, 0 extensions, only core Scratch opcodes.

## How it was verified
1. `tests/validate_sb3.py` — zip integrity, md5 of every asset, block graph (parent/next/inputs), variable/list/broadcast ids, custom-block definitions, hats, exactly four sprites, no extensions.
2. `tests/schema_check.js` — the **official `scratch-parser`** sb3 JSON-schema validator: **OK**.
3. `tests/run_tests.js` — loads the `.sb3` into the **real Scratch VM (`scratch-vm`) with the real WebGL renderer** (`scratch-render`, `scratch-svg-renderer`) in headless Chromium, with a virtual 30 fps clock and seeded random numbers. **56 tests, all passing on random seeds 1, 2, 3, 4 (and 1–5 earlier).**
4. `tests/bot_stats.js` — a bot plays complete games from keyboard input only: **wins 10/10 in 15–22 s** against a flood that needs ~126 s; an idle player loses.

Limitation (honest note): I could not drive the hosted editor at scratch.mit.edu from this environment, and sound output cannot be *heard* here; sounds were checked by decoding every WAV in a browser audio engine and by logging when each sound is played.

## Features verified
| Area | Verified |
|---|---|
| Structure | 4 sprites only; variables Score / Water Level / Game State / Vertical Speed; broadcasts Start Game / Supply Collected / Game Won / Game Lost; custom blocks; comments on scripts |
| Controls | walk speed & direction, 6-frame walk cycle, jump height (~91 px), no double jump, gravity, **never below the street or off-screen (4000-frame random-input fuzz)**, one-way platforms, all 5 platforms reachable |
| Supplies | always at one of 9 valid spots, never twice in a row, never under water, never collectable the instant it appears, never grabbable from the level below, +1 exactly once, score 0→10 and stops, burst animation, HUD costume updates |
| Flood | smooth constant rate (no jitter), reset to start every game, 6 wave costumes, darkens as it rises, reaches the top in ~125 s, exactly one `Game Lost` |
| Victory / defeat | win at 10; loss at the top; win-vs-lose race at 7 alignments always yields exactly one consistent ending; all logic stops after either |
| Restart | works after win and after loss; held SPACE cannot restart; early tap ignored; 3 games in a row with no duplicate loops; green flag mid-game or on an end screen resets cleanly |
| Sound | all WAVs decode; start / music loop / jump / splash / collect / alarm / win / lose play at the right moments; music stops at game end |
| Playability | bot wins every game; idle player loses |

## Bugs found by testing and fixed (examples)
Start-SPACE also jumped the runner; supply could spawn inside the touch range; HUD hid a supply spot; submerged runner invisible; double-collect from a spawn above the runner; platform crates grabbable from below (runner is 78 px tall, not 64); flood too fast for a child; flaky tests from unseeded randomness; bot "landing" detection bug.
