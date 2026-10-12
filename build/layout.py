"""Shared game layout (Scratch stage coordinates: x -240..240, y -180..180).

Both the artwork (backdrop) and the Scratch scripts use these numbers, so the
platforms you SEE are exactly the platforms the code lets you stand on.
"""

STAGE_W, STAGE_H = 480, 360

GROUND_Y = -115          # y position of the player's feet on the street
WATER_START = -168       # Water Level when a game starts (just above the screen bottom)
WATER_TOP = 172          # if the water surface reaches this, the player loses
WATER_RATE = 0.09        # Water Level gained per frame (30 frames per second): ~125 s from bottom to top

JUMP_SPEED = 14          # Vertical Speed given by a jump (reaches ~91 px)
GRAVITY = 1
MAX_FALL = 12
WALK_SPEED = 5
WADE_SPEED = 3           # speed while the feet are under water
LEDGE_GRAB = 12          # how far below a platform top still counts as landing

SUPPLIES_TO_WIN = 10

# (name, left x, right x, top y)  -- stand-on platforms, lowest first.
PLATFORMS = [
    ("Left balcony",   -228, -118, -45),
    ("Right balcony",   112,  226, -45),
    ("Middle roof",     -72,   42,  25),
    ("Upper left",     -232, -132,  95),
    ("Upper right",      98,  192,  95),
]

# Supply geometry.  The runner is 78 px tall; a supply's glow reaches GLOW px from
# its centre and bobs +-BOB px.  With HOVER = 40 a platform supply is easy to grab
# while standing on that platform, but a runner standing on the level below (70 px
# lower, helmet at +8) cannot touch it: 40 - 22 - 3 = 15 px above the platform.
RUNNER_HEIGHT = 78
GLOW = 22
BOB = 3
# a spot is "within reach of the runner's body" when (spot y - runner feet y) is in:
REACH_BELOW = -(GLOW + BOB)                 # supply is below the runner's feet by more than this -> safe
REACH_ABOVE = RUNNER_HEIGHT + GLOW + BOB    # supply is above the runner's helmet by more than this -> safe

HOVER = 40
SPOTS = [
    (-170, GROUND_Y + HOVER),
    (-60,  GROUND_Y + HOVER),
    (60,   GROUND_Y + HOVER),
    (170,  GROUND_Y + HOVER),
    (-185, -45 + HOVER),
    (165,  -45 + HOVER),
    (-15,  25 + HOVER),
    (-185, 95 + HOVER),
    (145,  95 + HOVER),
]

FEET_REACH = 8           # how far the feet may overhang a platform edge and still stand on it
SCREEN_EDGE = 225        # the runner cannot walk past this x
RUNNER_START_X = -10      # open street (nothing low overhead), centre of the screen

ONE_LEVEL = 170          # the next supply is at most this far (up/down) from the runner: about two balcony levels (70 px each)
