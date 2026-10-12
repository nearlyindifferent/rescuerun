# Loop 2 — Player Controls

## Agent 1 (Game Developer) — delivered
- Runner costumes drawn by `art.runner_svg()`: `idle`, `walk 1–6`, `jump`, `fall`, `cheer`, `oops`. Rotation centre is at the **feet**, so `y position` is the feet height.
- Custom blocks (visible under *My Blocks*): **Move Left Right**, **Find Floor**, **Jump And Gravity**, **Pick Costume**; the main loop is just those three blocks in a `repeat until Game State ≠ playing`.
- Physics: gravity −1 per frame, jump speed 14 (≈91 px), fall-speed cap 12, platform landing generated from `PLATFORMS`, one-way platforms (you can jump up through them), screen-edge limits, wading (slower) when feet are below `Water Level`.
- Controls: ← → walk, SPACE (or ↑) jump.

## Verified (real Scratch VM, `tests/run_tests.js`) — 16/16 pass
walk speed/direction, 6-frame walk cycle, idle, screen edges, both keys = no drift, jump height & exact return to ground, no mid-air double jump, landing on a balcony, walking off an edge, platform ladder (street → balcony → roof → upper platform on **both** sides), no pop-through from below, **4000-frame random-input fuzz (never below the street, never off-screen)**, wading speed, loop stops when `Game State` ≠ playing.

## Agent 2 (Visual Designer / Synthesizer) — review
Found by the tests, confirmed by me — **real bugs fixed in this loop:**
1. Pressing SPACE on the title also made the runner jump at game start. *Fix:* runner waits until SPACE is released before the loop starts.
2. The start position (x = −180) was directly under the left balcony, so that start-jump landed on the balcony. *Fix:* start at x = −10 (open street).

Visual review of the screenshot: the character is readable and friendly (helmet with cross, hi-vis vest, backpack); jump pose reads clearly; platform spacing (70 px) looks comfortable against a 91 px jump. Loose ends for later: arm/leg shapes are a little stiff (Loop 6); the placeholder background is flat (Loop 6).

## Corrections handed to Agent 1 for Loop 3
- A supply must never spawn on top of the runner or in the same place twice in a row, and must only appear at the nine `SPOTS` (all proven reachable above).
- Collection must feel good: sound, a pop/sparkle animation, and the score must go 0 → 10 exactly once per supply (no double counting while the collect animation plays).
- Score display must be a clean HUD (not a default variable watcher).
- Test: score increments exactly once per supply, supply respawns somewhere else, 10 collections in a row, no spawn inside the runner.
