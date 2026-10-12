"""Rescue Runner: the Scratch scripts for all four sprites + the stage."""
from sb3lib import *
from layout import *
import art


# ---- tiny helpers so the scripts below read like Scratch blocks ----
def setv(name, value):
    return blk("data_setvariableto", fields={"VARIABLE": name}, VALUE=value)


def chg(name, value):
    return blk("data_changevariableby", fields={"VARIABLE": name}, VALUE=value)


def keyp(key):
    return blk("sensing_keypressed", KEY_OPTION=key)


def AND(*conds):
    out = conds[0]
    for c in conds[1:]:
        out = blk("operator_and", OPERAND1=out, OPERAND2=c)
    return out


def OR(a, b):
    return blk("operator_or", OPERAND1=a, OPERAND2=b)


def NOT(a):
    return blk("operator_not", OPERAND=a)


def GT(a, b):
    return blk("operator_gt", OPERAND1=a, OPERAND2=b)


def LT(a, b):
    return blk("operator_lt", OPERAND1=a, OPERAND2=b)


def EQ(a, b):
    return blk("operator_equals", OPERAND1=a, OPERAND2=b)


def ADD(a, b):
    return blk("operator_add", NUM1=a, NUM2=b)


def SUB(a, b):
    return blk("operator_subtract", NUM1=a, NUM2=b)


def MUL(a, b):
    return blk("operator_multiply", NUM1=a, NUM2=b)


def DIV(a, b):
    return blk("operator_divide", NUM1=a, NUM2=b)


def MOD(a, b):
    return blk("operator_mod", NUM1=a, NUM2=b)


def JOIN(a, b):
    return blk("operator_join", STRING1=a, STRING2=b)


def MATH(op, a):
    return blk("operator_mathop", fields={"OPERATOR": op}, NUM=a)


def X():
    return blk("motion_xposition")


def Y():
    return blk("motion_yposition")


def IF(cond, then):
    return blk("control_if", CONDITION=cond, SUBSTACK=then)


def IFELSE(cond, then, other):
    return blk("control_if_else", CONDITION=cond, SUBSTACK=then, SUBSTACK2=other)


def play(sound):
    return blk("sound_play", SOUND_MENU=sound)


def broadcast(msg):
    return blk("event_broadcast", BROADCAST_INPUT=msg)


def costume(name):
    return blk("looks_switchcostumeto", COSTUME=name)


def build():
    P = Project()
    stage = P.stage

    # ---------------- global variables & broadcasts ----------------
    for name, val in [("Score", 0), ("Water Level", WATER_START), ("Game State", "title"), ("Vertical Speed", 0)]:
        stage.add_variable(name, val)
    for m in ["Start Game", "Supply Collected", "Game Won", "Game Lost"]:
        P.broadcast_id(m)

    # ---------------- Stage ----------------
    stage.add_costume("Flooded Village", art.backdrop(), "svg", 240, 180)
    stage.script(blk("event_whenflagclicked"),
                 [blk("looks_switchbackdropto", BACKDROP="Flooded Village")])

    # ---------------- Sprite 1: Rescue Runner ----------------
    runner = P.sprite("Rescue Runner")
    for nm, d in art.runner_costumes().items():
        runner.add_costume(nm, d, "svg", art.RW / 2, art.RH)     # rotation centre = feet
    runner.props.update(layerOrder=3, x=RUNNER_START_X, y=GROUND_Y, rotationStyle="left-right")
    for nm in ["Floor Y", "On Ground", "Moving", "Speed", "Walk Frame"]:
        runner.add_variable(nm, 0)

    # on the title screen the runner just stands there
    runner.script(blk("event_whenflagclicked"), [
        blk("motion_setrotationstyle", fields={"STYLE": "left-right"}),
        blk("motion_gotoxy", X=RUNNER_START_X, Y=GROUND_Y),
        blk("motion_pointindirection", DIRECTION=90),
        costume("idle"), blk("looks_show")],
        comment="The runner waits on the street while the title screen is showing.")

    runner.script(blk("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": "Start Game"}), [
        blk("motion_setrotationstyle", fields={"STYLE": "left-right"}),
        blk("motion_gotoxy", X=RUNNER_START_X, Y=GROUND_Y),
        blk("motion_pointindirection", DIRECTION=90),
        setv("Vertical Speed", 0), setv("On Ground", 1), setv("Walk Frame", 0),
        costume("idle"), blk("looks_show"),
        blk("control_wait_until", CONDITION=NOT(keyp("space"))),        # the SPACE that started the game must not also jump
        blk("control_repeat_until", CONDITION=NOT(EQ(var("Game State"), "playing")), SUBSTACK=[
            call("Move Left Right"),
            call("Jump And Gravity"),
            call("Pick Costume"),
        ])],
        comment="MAIN LOOP: every frame the runner moves, falls/jumps, then shows the right picture. It stops when Game State is no longer 'playing'.")

    runner.define("Move Left Right", [
        setv("Speed", WALK_SPEED),
        IF(LT(Y(), var("Water Level")), [setv("Speed", WADE_SPEED)]),
        setv("Moving", 0),
        IF(keyp("left arrow"), [
            blk("motion_pointindirection", DIRECTION=-90),
            blk("motion_changexby", DX=SUB(0, var("Speed"))),
            setv("Moving", 1)]),
        IF(keyp("right arrow"), [
            blk("motion_pointindirection", DIRECTION=90),
            blk("motion_changexby", DX=var("Speed")),
            setv("Moving", 1)]),
        IF(LT(X(), -SCREEN_EDGE), [blk("motion_setx", X=-SCREEN_EDGE)]),
        IF(GT(X(), SCREEN_EDGE), [blk("motion_setx", X=SCREEN_EDGE)]),
    ], comment="Arrow keys move the runner. Wading through water (feet below Water Level) is slower.")

    floor_checks = []
    for nm, left, right, top in PLATFORMS:        # lowest first, so the highest platform wins
        floor_checks.append(IF(AND(
            GT(X(), left - FEET_REACH), LT(X(), right + FEET_REACH),
            GT(Y(), top - LEDGE_GRAB), LT(var("Vertical Speed"), 1)),
            [setv("Floor Y", top)]))
    runner.define("Find Floor", [setv("Floor Y", GROUND_Y)] + floor_checks, warp=True,
                  comment="Works out how high the floor is under the runner: the street, or the top of a balcony/roof if the runner is above it and not rising.")

    runner.define("Jump And Gravity", [
        call("Find Floor"),
        chg("Vertical Speed", -GRAVITY),
        IF(LT(var("Vertical Speed"), -MAX_FALL), [setv("Vertical Speed", -MAX_FALL)]),
        blk("motion_changeyby", DY=var("Vertical Speed")),
        call("Find Floor"),
        IFELSE(LT(Y(), var("Floor Y")), [
            blk("motion_sety", Y=var("Floor Y")),
            setv("Vertical Speed", 0), setv("On Ground", 1)],
            [IF(GT(Y(), var("Floor Y")), [setv("On Ground", 0)])]),
        IF(AND(EQ(var("On Ground"), 1), OR(keyp("space"), keyp("up arrow"))), [
            setv("Vertical Speed", JUMP_SPEED), setv("On Ground", 0)]),
    ], comment="Gravity pulls the runner down every frame. The runner can never sink below the floor. SPACE (or up arrow) gives an upward Vertical Speed.")

    runner.define("Pick Costume", [
        IFELSE(EQ(var("On Ground"), 0), [
            IFELSE(GT(var("Vertical Speed"), 0), [costume("jump")], [costume("fall")])],
            [IFELSE(EQ(var("Moving"), 1), [
                chg("Walk Frame", 1),
                costume(JOIN("walk ", ADD(1, MOD(MATH("floor", DIV(var("Walk Frame"), 2)), 6))))],
                [costume("idle"), setv("Walk Frame", 0)])]),
    ], comment="Jumping, falling, walking (6 pictures in a loop) or standing still.")

    # ---------------- Sprite 2: Emergency Supply ----------------
    supply = P.sprite("Emergency Supply")
    d, cx, cy = art.supply()
    supply.add_costume("supply 1", d, "svg", cx, cy)
    supply.props.update(layerOrder=2, visible=False)
    supply.script(blk("event_whenflagclicked"), [blk("looks_hide")])

    # ---------------- Sprite 3: Rising Water ----------------
    water = P.sprite("Rising Water")
    d, cx, cy = art.water()
    water.add_costume("wave 1", d, "svg", cx, cy)
    water.props.update(layerOrder=4, x=0, y=WATER_START)
    water.script(blk("event_whenflagclicked"), [
        blk("motion_gotoxy", X=0, Y=var("Water Level")), blk("looks_show")])

    # ---------------- Sprite 4: Game Controller ----------------
    ctl = P.sprite("Game Controller")
    for nm, t, s in [("title", "RESCUE RUNNER", "Collect 10 supplies before the flood!"),
                     ("win", "YOU DID IT!", "Press SPACE to play again"),
                     ("lose", "FLOODED!", "Press SPACE to try again")]:
        d, cx, cy = art.screen(t, s)
        ctl.add_costume(nm, d, "svg", cx, cy)
    ctl.props.update(layerOrder=5, x=0, y=0)
    ctl.script(blk("event_whenflagclicked"), [
        blk("data_setvariableto", fields={"VARIABLE": "Game State"}, VALUE="title"),
        blk("data_setvariableto", fields={"VARIABLE": "Score"}, VALUE=0),
        blk("looks_switchcostumeto", COSTUME="title"),
        blk("motion_gotoxy", X=0, Y=0),
        blk("looks_show"),
        blk("control_wait_until", CONDITION=blk("sensing_keypressed", KEY_OPTION="space")),
        blk("data_setvariableto", fields={"VARIABLE": "Game State"}, VALUE="playing"),
        blk("looks_hide"),
        blk("event_broadcast", BROADCAST_INPUT="Start Game"),
    ])
    return P
