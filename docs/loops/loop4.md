# Loop 4 — Flood System

## Agent 1 (Game Developer) — delivered
- **Rising Water** sprite: 6 wave costumes (translucent gradient, foam crest, bubbles, light streaks). Rotation centre = the water *surface*, so `go to x:0 y:(Water Level)` puts the surface exactly at the variable.
- Flood script: `repeat until <Game State ≠ playing> or <Water Level > 172>` → `change Water Level by 0.14`, `go to`, and a `brightness` effect that darkens the water as it climbs. If the loop ends while still playing → `broadcast Game Lost`.
- Separate forever-script animates the waves (`next costume`, wait 0.12 s) — it keeps waving behind the win/lose screens.
- Wading: runner is slowed (speed 3 instead of 5) and drawn darker ("wet look") while its feet are below `Water Level`.

## Verified (real Scratch VM) — 30/30 pass (7 new)
Water idles at −168 on the title; rises exactly 0.14 px/frame with zero jitter and the sprite follows the variable; all 6 wave costumes cycle; brightness falls to ≈ −25 at the top; **full-length run: flood reaches the top in 70–95 s (design ≈ 80 s), `Game Lost` is broadcast exactly once and the water stops**; supplies are never spawned under water (30 spawns at a raised level); `Game Lost` within a moment when the level is 171.

## Agent 2 (Visual Designer / Synthesizer) — review
From the three flood screenshots (low / mid / high):
1. **Problem:** with the water drawn *in front of* the runner, a submerged runner almost vanished (two translucent layers ≈ 95 % opaque). A child must always see their character. *Fix:* water moved **behind** the runner and supplies (layer order Stage < Water < Supply < Runner < Controller), water opacity lightened a little so platforms still show through, and the runner gets a darker "wet" look while wading so the water still matters visually.
2. Waves, depth gradient and darkening read as "danger rising" — approved.
3. Note for Loop 6: the platforms and sky are still flat placeholders; add the flooded-village backdrop.

## Corrections handed to Agent 1 for Loop 5
- `Game Won` / `Game Lost` must be handled **only if `Game State` is still `playing`** (so a win and a loss in the same frame can never both happen).
- After a win/lose: stop the music/sounds, show the screen costume, require SPACE to be *released* then pressed again before restarting (so a held jump key cannot instantly restart).
- Restart must fully reset: Score, Water Level, supply, runner, HUD, and every loop must start fresh (no leftover scripts).
- Test: win, lose, win-vs-lose race, restart twice, restart from both end screens, green flag in the middle of a game.
