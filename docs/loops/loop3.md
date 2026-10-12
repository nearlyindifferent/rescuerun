# Loop 3 — Supply Collection

## Agent 1 (Game Developer) — delivered
- **Emergency Supply** sprite: 4 glow/pulse costumes + `burst`; it bobs with `sin` and glows while waiting.
- Two lists, `Spot X` / `Spot Y`, hold the nine places a supply may appear (street + every platform). Custom blocks: **Setup Spots, Check Spot, Pick Spot, Pop In, Float, Collect Supply**.
- A spot is rejected if it is the one just used, is under water, or is right on top of the runner.
- Collecting: `change Score by 1` → `broadcast Supply Collected` → starburst animation → hide → next supply.
- **Game Controller**: scoreboard drawn as costumes `Score 0 … Score 10` (progress bar + number) and shown by `switch costume to (join "Score " Score)`. New custom block **Start New Game** resets Score, Water Level, Vertical Speed and Game State *before* broadcasting `Start Game`.

## Verified (real Scratch VM) — 23/23 pass (7 new)
Every spot lies on the street or on a platform; lists match; score 0 + HUD at start; supply floats and cycles 4 glow frames; touching it gives exactly +1 (no double counting while standing there); starburst plays; supply reappears elsewhere; 10 collections count 1…10 and stay at 10; 60 consecutive respawns are always valid, never repeat, never on top of the runner; spawns use all the map.

## Agent 2 (Visual Designer / Synthesizer) — review
Bugs found and fixed inside this loop:
1. **Instant free point:** a supply could spawn 50 px from the runner — inside the touch range (glow + body) — so it was collected the moment it appeared. *Fix:* exclusion zone widened to 70 px horizontally / 50 px vertically.
2. **HUD covered a supply spot:** the top-left scoreboard sat on top of the upper-left spot. *Fix:* scoreboard moved to top-centre (no spot or platform hidden).
3. Test-suite note: `set Score to 0` stores the *text* "0" in Scratch; the game compares numerically, so the test was changed to compare as a number (not a game bug).

Visual review: crate is recognisable as a first-aid kit, the glow pulse is gentle; HUD is clean and readable.

## Corrections handed to Agent 1 for Loop 4
- Water must rise **smoothly** from `Water Level` = −168 at a rate that leaves a comfortable ~80 s, be frame-rate independent of the other sprites, and animate its surface (≥ 6 wave costumes).
- Water must reset on every restart and never stay "stuck" at the previous level.
- Danger feedback: the water should darken as it climbs.
- Test: rate, reset, top reached → `Game Lost` is broadcast exactly once, wave costumes cycle, supplies are never placed under water while higher spots exist.
