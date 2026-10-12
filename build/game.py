"""Rescue Runner: the Scratch scripts for all four sprites + the stage."""
from sb3lib import *
from layout import *
import art
import audio


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
    SND = audio.all_sounds()


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
    for nm in ["Floor Y", "On Ground", "Moving", "Speed", "Walk Frame", "Was Wet"]:
        runner.add_variable(nm, 0)
    runner.add_sound("jump", SND["jump"])
    runner.add_sound("splash", SND["splash"])

    # on the title screen the runner just stands there
    runner.script(blk("event_whenflagclicked"), [
        blk("motion_setrotationstyle", fields={"STYLE": "left-right"}),
        blk("motion_gotoxy", X=RUNNER_START_X, Y=GROUND_Y),
        blk("motion_pointindirection", DIRECTION=90),
        costume("idle"), blk("looks_show")],
        comment="The runner waits on the street while the title screen is showing.")

    runner.script(blk("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": "Start Game"}), [
        stop("other scripts in sprite"),                      # end any leftover cheer/oops script from the last game
        blk("motion_setrotationstyle", fields={"STYLE": "left-right"}),
        blk("motion_gotoxy", X=RUNNER_START_X, Y=GROUND_Y),
        blk("motion_pointindirection", DIRECTION=90),
        setv("Vertical Speed", 0), setv("On Ground", 1), setv("Walk Frame", 0),
        blk("looks_cleargraphiceffects"),
        costume("idle"), blk("looks_show"),
        blk("control_wait_until", CONDITION=NOT(keyp("space"))),        # the SPACE that started the game must not also jump
        blk("control_repeat_until", CONDITION=NOT(EQ(var("Game State"), "playing")), SUBSTACK=[
            call("Move Left Right"),
            call("Jump And Gravity"),
            call("Pick Costume"),
        ])],
        comment="MAIN LOOP: every frame the runner moves, falls/jumps, then shows the right picture. It stops when Game State is no longer 'playing'.")

    runner.script(blk("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": "Game Won"}), [
        costume("cheer"), blk("looks_cleargraphiceffects"),
        blk("control_repeat_until", CONDITION=EQ(var("On Ground"), 1), SUBSTACK=[call("Apply Gravity")]),
        blk("control_repeat", TIMES=4, SUBSTACK=[
            blk("control_repeat", TIMES=5, SUBSTACK=[blk("motion_changeyby", DY=5)]),
            blk("control_repeat", TIMES=5, SUBSTACK=[blk("motion_changeyby", DY=-5)])])],
        comment="VICTORY: the runner finishes landing, cheers, and hops for joy.")

    runner.script(blk("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": "Game Lost"}), [
        costume("oops"),
        blk("control_repeat_until", CONDITION=EQ(var("On Ground"), 1), SUBSTACK=[call("Apply Gravity")])],
        comment="DEFEAT: the runner finishes landing and looks worried.")

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

    runner.define("Apply Gravity", [
        call("Find Floor"),
        chg("Vertical Speed", -GRAVITY),
        IF(LT(var("Vertical Speed"), -MAX_FALL), [setv("Vertical Speed", -MAX_FALL)]),
        blk("motion_changeyby", DY=var("Vertical Speed")),
        call("Find Floor"),
        IFELSE(LT(Y(), var("Floor Y")), [
            blk("motion_sety", Y=var("Floor Y")),
            setv("Vertical Speed", 0), setv("On Ground", 1)],
            [IF(GT(Y(), var("Floor Y")), [setv("On Ground", 0)])]),
    ], comment="Gravity pulls the runner down every frame. The runner can never sink below the floor.")

    runner.define("Jump And Gravity", [
        call("Apply Gravity"),
        IF(AND(EQ(var("On Ground"), 1), OR(keyp("space"), keyp("up arrow"))), [
            setv("Vertical Speed", JUMP_SPEED), setv("On Ground", 0), play("jump")]),
    ], comment="Gravity, plus: SPACE (or up arrow) while standing on something gives an upward Vertical Speed.")

    runner.define("Pick Costume", [
        IFELSE(EQ(var("On Ground"), 0), [
            IFELSE(GT(var("Vertical Speed"), 0), [costume("jump")], [costume("fall")])],
            [IFELSE(EQ(var("Moving"), 1), [
                chg("Walk Frame", 1),
                costume(JOIN("walk ", ADD(1, MOD(MATH("floor", DIV(var("Walk Frame"), 2)), 6))))],
                [costume("idle"), setv("Walk Frame", 0)])]),
        IFELSE(LT(Y(), var("Water Level")),
               [blk("looks_seteffectto", fields={"EFFECT": "brightness"}, VALUE=-18),
                IF(EQ(var("Was Wet"), 0), [play("splash"), setv("Was Wet", 1)])],
               [blk("looks_seteffectto", fields={"EFFECT": "brightness"}, VALUE=0), setv("Was Wet", 0)]),
    ], comment="Jumping, falling, walking (6 pictures in a loop) or standing still. A runner standing in the water looks darker and wet.")

    # ---------------- Sprite 2: Emergency Supply ----------------
    supply = P.sprite("Emergency Supply")
    for nm, d in art.supply_costumes().items():
        supply.add_costume(nm, d, "svg", art.SW / 2, art.SW / 2)
    supply.props.update(layerOrder=2, visible=False)
    for nm in ["Spot Index", "Last Spot", "Tries", "Spot OK", "Bob", "Base Y"]:
        supply.add_variable(nm, 0)
    supply.add_sound("collect", SND["collect"])
    supply.add_list("Spot X", [x for x, y in SPOTS])
    supply.add_list("Spot Y", [y for x, y in SPOTS])

    def item_of(lst, idx):
        return blk("data_itemoflist", fields={"LIST": lst}, INDEX=idx)

    supply.script(blk("event_whenflagclicked"), [
        blk("looks_hide"), call("Setup Spots")],
        comment="The supply stays hidden until the game starts.")

    supply.define("Setup Spots",
        [blk("data_deletealloflist", fields={"LIST": "Spot X"}),
         blk("data_deletealloflist", fields={"LIST": "Spot Y"})] +
        [blk("data_addtolist", fields={"LIST": "Spot X"}, ITEM=x) for x, y in SPOTS] +
        [blk("data_addtolist", fields={"LIST": "Spot Y"}, ITEM=y) for x, y in SPOTS],
        comment="Two lists hold every place a supply may appear (x and y). Each spot is on the street or on a balcony/roof the runner can reach.")

    supply.script(blk("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": "Start Game"}), [
        blk("looks_hide"), setv("Last Spot", 0), setv("Bob", 0),
        blk("control_wait", DURATION=0.5),
        blk("control_repeat_until", CONDITION=OR(NOT(EQ(var("Game State"), "playing")), EQ(var("Score"), SUPPLIES_TO_WIN)), SUBSTACK=[
            call("Pick Spot"),
            call("Pop In"),
            blk("control_repeat_until", CONDITION=OR(blk("sensing_touchingobject", TOUCHINGOBJECTMENU="Rescue Runner"),
                                                     NOT(EQ(var("Game State"), "playing"))), SUBSTACK=[
                call("Float")]),
            IF(EQ(var("Game State"), "playing"), [call("Collect Supply")]),
        ]),
        blk("looks_hide")],
        comment="Show one supply at a time. Wait until the runner touches it, collect it, then show the next one.")

    supply.define("Check Spot", [
        setv("Spot OK", 1),
        IF(EQ(var("Spot Index"), var("Last Spot")), [setv("Spot OK", 0)]),
        IF(LT(item_of("Spot Y", var("Spot Index")), ADD(var("Water Level"), 5)), [setv("Spot OK", 0)]),
        IF(AND(
            LT(MATH("abs", SUB(item_of("Spot X", var("Spot Index")), blk("sensing_of", fields={"PROPERTY": "x position"}, OBJECT="Rescue Runner"))), 70),
            GT(SUB(item_of("Spot Y", var("Spot Index")), blk("sensing_of", fields={"PROPERTY": "y position"}, OBJECT="Rescue Runner")), REACH_BELOW),
            LT(SUB(item_of("Spot Y", var("Spot Index")), blk("sensing_of", fields={"PROPERTY": "y position"}, OBJECT="Rescue Runner")), REACH_ABOVE)),
            [setv("Spot OK", 0)]),
        IF(AND(LT(var("Tries"), 12),
               GT(MATH("abs", SUB(item_of("Spot Y", var("Spot Index")), ADD(blk("sensing_of", fields={"PROPERTY": "y position"}, OBJECT="Rescue Runner"), HOVER))), ONE_LEVEL)),
           [setv("Spot OK", 0)]),
    ], warp=True, comment="A spot is OK if it is not the one we just used, is not under water, and is not within reach of the runner's body (so a new supply can never be collected the instant it appears).")

    supply.define("Pick Spot", [
        setv("Tries", 0), setv("Spot OK", 0),
        setv("Spot Index", blk("operator_random", FROM=1, TO=blk("data_lengthoflist", fields={"LIST": "Spot X"}))),
        blk("control_repeat_until", CONDITION=OR(EQ(var("Spot OK"), 1), GT(var("Tries"), 24)), SUBSTACK=[
            chg("Tries", 1),
            IFELSE(LT(var("Tries"), 12),
                   [setv("Spot Index", blk("operator_random", FROM=1, TO=blk("data_lengthoflist", fields={"LIST": "Spot X"})))],
                   [setv("Spot Index", ADD(MOD(var("Spot Index"), blk("data_lengthoflist", fields={"LIST": "Spot X"})), 1))]),
            call("Check Spot")]),
        setv("Last Spot", var("Spot Index")),
        setv("Base Y", item_of("Spot Y", var("Spot Index"))),
        blk("motion_gotoxy", X=item_of("Spot X", var("Spot Index")), Y=var("Base Y")),
    ], comment="Try random spots first; if none is good, check every spot in order, so a good spot is always found if one exists.")

    supply.define("Pop In", [
        costume("supply 1"), blk("looks_setsizeto", SIZE=40),
        blk("looks_seteffectto", fields={"EFFECT": "ghost"}, VALUE=80), blk("looks_show"),
        blk("control_repeat", TIMES=5, SUBSTACK=[
            blk("looks_changesizeby", CHANGE=12),
            blk("looks_changeeffectby", fields={"EFFECT": "ghost"}, CHANGE=-16)]),
    ])

    supply.define("Float", [
        chg("Bob", 15),
        setv("Bob", MOD(var("Bob"), 360)),
        blk("motion_sety", Y=ADD(var("Base Y"), MUL(BOB, MATH("sin", var("Bob"))))),
        costume(JOIN("supply ", ADD(1, MATH("floor", DIV(var("Bob"), 90))))),
    ], comment="The supply bobs up and down and glows (4 pictures) while it waits to be collected.")

    supply.define("Collect Supply", [
        chg("Score", 1),
        play("collect"),
        broadcast("Supply Collected"),
        costume("burst"),
        blk("control_repeat", TIMES=6, SUBSTACK=[
            blk("looks_changesizeby", CHANGE=10),
            blk("looks_changeeffectby", fields={"EFFECT": "ghost"}, CHANGE=17)]),
        blk("looks_hide"),
        blk("looks_seteffectto", fields={"EFFECT": "ghost"}, VALUE=0),
        blk("looks_setsizeto", SIZE=100),
    ], comment="Score goes up by 1, everyone is told 'Supply Collected', and a starburst pops and fades.")

    # ---------------- Sprite 3: Rising Water ----------------
    water = P.sprite("Rising Water")
    for nm, d in art.water_costumes().items():
        water.add_costume(nm, d, "svg", art.WCX, art.WCY)       # rotation centre = the water surface
    water.add_sound("alarm", SND["alarm"])
    water.add_variable("Warned", 0)
    water.props.update(layerOrder=1, x=0, y=WATER_START)   # behind the runner and supplies: the player is always visible

    water.script(blk("event_whenflagclicked"), [
        setv("Water Level", WATER_START),
        blk("looks_cleargraphiceffects"),
        blk("motion_gotoxy", X=0, Y=var("Water Level")), costume("wave 1"), blk("looks_show")],
        comment="On the title screen the water sits at the bottom of the screen.")

    water.script(blk("event_whenflagclicked"), [
        blk("control_forever", SUBSTACK=[
            blk("looks_nextcostume"), blk("control_wait", DURATION=0.12)])],
        comment="Wave animation: 6 pictures of the water surface, forever.")

    water.script(blk("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": "Start Game"}), [
        blk("looks_cleargraphiceffects"), setv("Warned", 0),
        blk("motion_gotoxy", X=0, Y=var("Water Level")), blk("looks_show"),
        blk("control_repeat_until", CONDITION=OR(NOT(EQ(var("Game State"), "playing")), GT(var("Water Level"), WATER_TOP)), SUBSTACK=[
            chg("Water Level", WATER_RATE),
            blk("motion_gotoxy", X=0, Y=var("Water Level")),
            IF(AND(GT(var("Water Level"), 60), EQ(var("Warned"), 0)), [play("alarm"), setv("Warned", 1)]),
            IF(AND(GT(var("Water Level"), 130), EQ(var("Warned"), 1)), [play("alarm"), setv("Warned", 2)]),
            blk("looks_seteffectto", fields={"EFFECT": "brightness"},
                VALUE=MUL(DIV(SUB(var("Water Level"), WATER_START), WATER_TOP - WATER_START), -25))]),
        IF(EQ(var("Game State"), "playing"), [broadcast("Game Lost")])],
        comment="THE FLOOD: every frame the water rises a little and gets darker. If it reaches the top of the screen while we are still playing, the game is lost.")

    # ---------------- Sprite 4: Game Controller ----------------
    ctl = P.sprite("Game Controller")
    for nm, d in [("title", art.title_card()), ("win", art.win_card()), ("lose", art.lose_card())]:
        ctl.add_costume(nm, d, "svg", 240, 180)
    for n in range(SUPPLIES_TO_WIN + 1):
        ctl.add_costume("Score %d" % n, art.hud(n), "svg", 240, 180)
    for nm in ["start", "win", "lose", "music"]:
        ctl.add_sound(nm, SND[nm])
    ctl.props.update(layerOrder=4, x=0, y=0)

    ctl.script(blk("event_whenflagclicked"), [
        setv("Game State", "title"), setv("Score", 0),
        costume("title"), blk("motion_gotoxy", X=0, Y=0), blk("looks_show"),
        blk("control_wait_until", CONDITION=keyp("space")),
        call("Start New Game")],
        comment="Green flag: show the title card and wait for SPACE.")

    ctl.define("Start New Game", [
        setv("Score", 0),
        setv("Water Level", WATER_START),
        setv("Vertical Speed", 0),
        setv("Game State", "playing"),
        broadcast("Start Game")],
        comment="Reset everything FIRST (score, water, speed, state), then tell all the sprites to start.")

    ctl.script(blk("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": "Start Game"}), [
        costume("Score 0"), blk("motion_gotoxy", X=0, Y=0), blk("looks_show"), play("start")],
        comment="The scoreboard is a costume: 'Score 0' ... 'Score 10'.")

    ctl.script(blk("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": "Start Game"}), [
        blk("sound_setvolumeto", VOLUME=45),
        blk("control_wait", DURATION=0.6),
        blk("control_repeat_until", CONDITION=NOT(EQ(var("Game State"), "playing")), SUBSTACK=[
            blk("sound_playuntildone", SOUND_MENU="music")])],
        comment="Background music loops while the game is being played.")

    ctl.script(blk("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": "Supply Collected"}), [
        costume(JOIN("Score ", var("Score"))),
        IF(AND(EQ(var("Score"), SUPPLIES_TO_WIN), EQ(var("Game State"), "playing")), [broadcast("Game Won")])],
        comment="Update the scoreboard. The 10th supply wins the game.")

    ctl.script(blk("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": "Game Won"}), [
        IF(EQ(var("Game State"), "playing"), [
            setv("Game State", "won"),
            blk("sound_stopallsounds"), blk("sound_setvolumeto", VOLUME=80), play("win"),
            costume("win"),
            call("Wait For Restart")])],
        comment="VICTORY screen. It only happens if the game was still 'playing', so a win and a loss can never both happen.")

    ctl.script(blk("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": "Game Lost"}), [
        IF(EQ(var("Game State"), "playing"), [
            setv("Game State", "lost"),
            blk("sound_stopallsounds"), blk("sound_setvolumeto", VOLUME=80), play("lose"),
            costume("lose"),
            call("Wait For Restart")])],
        comment="DEFEAT screen: the flood reached the top.")

    ctl.define("Wait For Restart", [
        blk("control_wait", DURATION=1),
        blk("control_wait_until", CONDITION=NOT(keyp("space"))),
        blk("control_wait_until", CONDITION=keyp("space")),
        call("Start New Game")],
        comment="Wait 1 second, wait for SPACE to be let go (so a held jump key can't restart), then wait for a new SPACE press.")
    return P
