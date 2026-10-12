# Loop 5 — Victory and Defeat

## Agent 1 (Game Developer) — delivered
- **Game Controller** owns the game state (`title → playing → won / lost`). `Supply Collected` updates the scoreboard and broadcasts `Game Won` when `Score = 10`; the water broadcasts `Game Lost` when it reaches the top.
- `Game Won` / `Game Lost` handlers run **only `if Game State = playing`**, so a win and a loss in the same frame can never both happen.
- **Wait For Restart** (custom block): wait 1 s → wait until SPACE is *released* → wait until SPACE is *pressed* → **Start New Game** (which resets Score, Water Level, Vertical Speed and Game State *before* it broadcasts `Start Game`).
- **Runner** finishes landing (new custom block **Apply Gravity**, split out of Jump And Gravity) and then cheers + hops (win) or looks worried (lose); its `Start Game` script begins with `stop other scripts in sprite` so no leftover celebration can interfere with a restart.
- All loops end when `Game State ≠ playing`, so supply, water, runner and score logic really stop.

## Verified (real Scratch VM; seeded random numbers so every run is reproducible)
- Win screen, state, cheer, supply hidden, water frozen, keys ignored, score stays 10; lose screen, state, worried runner, water frozen, score unchanged; defeat while jumping (runner lands); hop returns the runner exactly to its surface.
- **Win-vs-lose race at 7 different frame alignments:** always exactly one ending, always consistent, never flips.
- Restart after victory and after defeat (everything reset: score, water, HUD, runner, supply, controls work); a quick tap in the first second is ignored; a **held SPACE never restarts** (needs release + new press).
- Three games in a row (win, lose, win): one `Start Game` per game, one water loop (rate not doubled), ≤ 4 threads alive.
- Green flag mid-game and green flag on the win screen: back to the title, SPACE starts exactly one game (the old "waiting for restart" script is cancelled).
- **Bot player** (reads the screen, presses keys, climbs balconies/roofs): wins all 10 supplies; **idle player loses.**
- Whole suite repeated with 5 different random seeds: 52/52 each.

## Agent 2 (Visual Designer / Synthesizer) — review
Real problems found in this loop (all fixed):
1. **Double-collect bug (found by changing the random seed).** The runner stood on the street at x = 170 and the next supply spawned on the balcony at x = 165, 70 px above. The supply's bobbing glow reaches down to the runner's helmet, so it was collected the instant it appeared. *Fix:* `Check Spot` now rejects any spot within 70 px horizontally **and** within the runner's whole body height window (−37 … +101 px), not just the same level.
2. **Flaky tests** were caused by the real random generator; the harness now seeds it.
3. **Difficulty tuning (found by the bot).** A bot that plays like a person wins in 15–22 s (20/20 seeds; median 18 s). Two real design changes came out of this: (a) supplies now hover 40 px (runner is 78 px tall, glow 22 px, bob ±3) so a platform crate **cannot be grabbed from the level below** without jumping; (b) the next supply is never more than two levels away from the runner, and `Pick Spot` falls back to scanning every spot so it can never get stuck. The flood was tuned to **0.09 px/frame (≈ 125 s)** so a perfect player sees the water barely rise while a typical child (3–5× slower) sees it climb into the balcony zone.
3b. (Bot bug, not a game bug) the bot first mistook "passing the balcony height while rising" for "landed"; it now uses the runner's own on-ground flag.
4. Held-SPACE test was timing-sensitive (the key was pressed *after* the 1 s wait, which is a legitimate restart). Test redesigned: key is held *before* the game ends.

Visual notes (screens are still placeholder text cards): the win/lose cards need real artwork, confetti, and the title should show controls — scheduled for Loop 6.

## Corrections handed to Agent 1 for Loop 6
- Replace the placeholder backdrop with a flooded-village scene whose balconies/roof are drawn **exactly** on the `PLATFORMS` coordinates (art = collision).
- New title / win / lose cards, controls hint on the scoreboard.
- Sound: jump, collect, start jingle, win, lose, flood alarm, background music (stop on game end).
- Keep every costume light (SVG) and verify the file still loads and every earlier test still passes.
