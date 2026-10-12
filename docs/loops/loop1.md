# Loop 1 — Foundation

## Agent 1 (Game Developer) — delivered
- `build/sb3lib.py`: writer for genuine Scratch 3 projects (real opcodes, inputs, fields, custom blocks, variables, lists, broadcasts, costumes, sounds).
- Project with the Stage + **exactly four sprites**: Rescue Runner, Emergency Supply, Rising Water, Game Controller.
- Global variables `Score`, `Water Level`, `Game State`, `Vertical Speed`; broadcasts `Start Game`, `Supply Collected`, `Game Won`, `Game Lost`.
- Title screen (Game Controller costume) → wait for SPACE → set `Game State = playing` → broadcast `Start Game`.
- Placeholder (simple-shape) artwork, drawn from shared coordinates in `build/layout.py` so the art and the code can never disagree about platform positions.
- Test tooling: `tests/validate_sb3.py` (structure), `tests/schema_check.js` (official `scratch-parser`), `tests/harness` (real `scratch-vm` + `scratch-render` in headless Chromium, virtual 30 fps clock).

## Verified
- `scratch-parser` accepts the file; structural validator passes (5 targets, 24 blocks, no extensions, only core opcodes).
- Loads in the real Scratch VM; green flag shows the title; SPACE sets `Game State` to `playing`; no runtime errors.

## Agent 2 (Visual Designer / Synthesizer) — review of the screenshot
1. The title card is a big dark rectangle that hides the runner and the platforms. **Fix later (Loop 6):** smaller, friendlier card with key-cap icons.
2. The runner is drawn *behind* the card while the title shows. Acceptable, but make sure the runner is idle-posed and visible beside the card.
3. Placeholder art has no clouds, buildings, or water waves yet — expected, scheduled for Loop 6.
4. `Game State` is set **before** the `Start Game` broadcast. Good: this avoids a start-up race where other sprites' loops would see the old state. **Keep this pattern** for every restart.

## Corrections handed to Agent 1 for Loop 2
- Put the runner's rotation centre at its **feet** so `y position` = feet height.
- Use **custom blocks** (`Move Left Right`, `Jump And Gravity`) so the main loop reads like a sentence.
- Landing logic must come from `PLATFORMS` in `layout.py`; add a downward-speed cap so the runner can never skip through the ground or a platform.
- Test: jump heights, edges of the screen, falling off a platform, and holding both arrow keys.
