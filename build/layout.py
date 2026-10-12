"""Shared game layout (Scratch stage coordinates: x -240..240, y -180..180).

Both the artwork (backdrop) and the Scratch scripts use these numbers, so the
platforms you SEE are exactly the platforms the code lets you stand on.
"""

STAGE_W, STAGE_H = 480, 360

GROUND_Y = -115          # y position of the player's feet on the street
WATER_START = -168       # Water Level when a game starts (just above the screen bottom)
WATER_TOP = 172          # if the water surface reaches this, the player loses
WATER_RATE = 0.14        # Water Level gained per frame (30 frames per second)

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

# Supply spots: (x, y of the package centre).  A package floats 24 px above
# the surface it belongs to, so the runner can grab it while standing there.
HOVER = 24
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
