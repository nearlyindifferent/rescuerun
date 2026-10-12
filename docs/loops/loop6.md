# Loop 6 — Visual Polish

## Agent 1 (Game Developer) — delivered
- **Flooded-village backdrop** (SVG): gradient sky, sun, clouds, distant skyline, two tall buildings with wooden balconies, a green shop whose flat roof is the middle platform, street, lamp posts, hydrant, flood-warning sign. Platforms are drawn from the same `PLATFORMS` numbers the scripts use (art = collision).
- New **title**, **win** (stars + confetti) and **lose** (water drop) cards, controls hint on the scoreboard.
- **Sounds** (synthesised, no copyrighted audio): jump, splash (when the runner gets wet), collect chime, flood alarm (water at 60 and 130), start jingle, win fanfare, lose jingle, looping background music that stops when the game ends.
- Supply glow tightened (22 px) to match the gameplay geometry.

## Verified
Sound assets decode in a real browser audio engine; each sound plays at the correct moment; music loops and stops after win/lose; one splash per soaking; full suite 56/56 (seed 1). Screenshots of title, play, flood, win, lose rendered by the real Scratch renderer: `docs/screenshots/`.

## Agent 2 (Visual Designer / Synthesizer) — review
Approved: consistent cartoon style (thick outlines, warm/cool palette), readable at stage size, platforms clearly distinguishable from buildings, water darkening shows danger, end cards are friendly. Defects found and fixed: controls hint overflowed its pill (shortened and resized); supply glow radius reduced so it matches the hit area.

## Corrections for Loop 7
- Full regression on several random seeds, bot playthroughs, structure + schema validation, inspect `project.json` for non-core opcodes/extensions, final screenshots, README.
