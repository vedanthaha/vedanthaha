from PIL import Image, ImageDraw, ImageFont
import math, os, random

# Hand-built pixel scene. No generated artwork, no gradients, no external assets.
# Drawn on a tiny canvas and nearest-neighbour scaled for a deliberate pixel grid.

S = 4
W, H = 240, 135
FRAMES = 96
BG = (9, 10, 10)
INK = (226, 226, 216)
DIM = (104, 106, 101)
GRID = (31, 33, 32)
PANEL = (17, 19, 18)
GREEN = (118, 154, 112)
SKIN = (214, 176, 136)
HAIR = (43, 35, 31)
SHIRT = (210, 210, 199)
PANTS = (72, 74, 71)
BLUE = (112, 133, 153)

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F = lambda n: ImageFont.truetype(font_path, n)
B = lambda n: ImageFont.truetype(bold_path, n)

def rect(d, x, y, w, h, c):
    d.rectangle((x, y, x+w-1, y+h-1), fill=c)

def text(d, xy, s, f, c):
    d.text(xy, s, font=f, fill=c)

def person(d, x, y, pose="walk", frame=0):
    # 16x30-ish hand-authored sprite.
    bob = 1 if pose == "walk" and frame % 8 in (2,3,4) else 0
    y += bob

    # hair/head
    rect(d,x+3,y-15,8,7,SKIN)
    rect(d,x+3,y-16,8,2,HAIR)
    rect(d,x+2,y-15,2,4,HAIR)
    rect(d,x+10,y-14,1,2,HAIR)

    # body
    rect(d,x+2,y-8,10,12,SHIRT)

    if pose == "sit":
        rect(d,x+3,y+4,5,5,PANTS)
        rect(d,x+8,y+4,5,4,PANTS)
        rect(d,x+9,y+7,8,3,PANTS)
        rect(d,x-1,y-6,5,3,SHIRT)
        rect(d,x-3,y-4,3,2,SKIN)
        rect(d,x+10,y-6,5,3,SHIRT)
        rect(d,x+14,y-4,3,2,SKIN)
    elif pose == "work":
        # arms reaching toward keyboard
        rect(d,x-1,y-6,5,3,SHIRT)
        rect(d,x-3,y-4,3,2,SKIN)
        rect(d,x+10,y-6,7,3,SHIRT)
        rect(d,x+16,y-4,3,2,SKIN)
        rect(d,x+3,y+4,5,8,PANTS)
        rect(d,x+8,y+4,5,8,PANTS)
        rect(d,x+2,y+11,7,2,INK)
        rect(d,x+8,y+11,7,2,INK)
    elif pose == "wave":
        rect(d,x-1,y-6,5,3,SHIRT)
        rect(d,x-3,y-4,3,2,SKIN)
        rect(d,x+10,y-7,3,3,SHIRT)
        lift = int(round(2*math.sin(frame*0.9)))
        rect(d,x+12,y-11-lift,3,5,SKIN)
        rect(d,x+13,y-14-lift,2,3,SKIN)
        rect(d,x+3,y+4,5,9,PANTS)
        rect(d,x+8,y+4,5,9,PANTS)
        rect(d,x+1,y+12,7,2,INK)
        rect(d,x+8,y+12,7,2,INK)
    else:
        # walking legs alternate
        step = -1 if frame % 8 < 4 else 1
        rect(d,x+2,y+4,4,9,PANTS)
        rect(d,x+8,y+4,4,8,PANTS)
        rect(d,x+1+step,y+12,6,2,INK)
        rect(d,x+7-step,y+12,6,2,INK)
        rect(d,x-2,y-6,4,3,SHIRT)
        rect(d,x-4,y-4,3,2,SKIN)
        rect(d,x+11,y-6,4,3,SHIRT)
        rect(d,x+14,y-4,3,2,SKIN)

def laptop(d, x, y, open_amt=1.0):
    # Chunky 12-bit laptop, drawn from rectangles.
    rect(d,x,y,24,12,PANTS)
    rect(d,x+2,y+2,20,8,(24,28,27))
    # tiny terminal pixels
    for i in range(7):
        rect(d,x+4+i*2,y+4,1,1,GREEN if i < 4 else DIM)
    rect(d,x-2,y+12,28,2,INK)

def desk(d):
    rect(d,148,91,48,3,INK)
    rect(d,151,94,3,27,DIM)
    rect(d,191,94,3,27,DIM)
    laptop(d,160,76)
    rect(d,181,84,6,6,BLUE)
    rect(d,182,85,4,4,PANEL)
    rect(d,200,86,7,7,GREEN)
    rect(d,202,84,3,3,GREEN)

def chair(d, x, y):
    rect(d,x,y,12,3,DIM)
    rect(d,x+1,y-13,10,3,DIM)
    rect(d,x+2,y-10,8,10,PANEL)
    rect(d,x+4,y+3,2,11,DIM)
    rect(d,x+1,y+13,8,2,DIM)

def terminal(d, x, y, phase):
    rect(d,x,y,57,31,PANEL)
    rect(d,x+1,y+1,55,2,DIM)
    text(d,(x+4,y+5),"~/vedant",F(5),DIM)
    lines=[
        "> build --watch",
        "  compiling...",
        "  interface ready",
        "  ship.",
    ]
    for i,line in enumerate(lines):
        shown = min(len(line), max(0, int(phase*len(line)*1.5)-i*7))
        if shown:
            text(d,(x+4,y+12+i*5),line[:shown],F(5),GREEN if i in (0,3) else INK)

def project_board(d, x, y, phase):
    rect(d,x,y,57,31,PANEL)
    text(d,(x+4,y+4),"WORK",B(6),INK)
    cards=[("BLINKY",GREEN),("CIVIFIX",BLUE),("DROP",INK),("DAILYS",DIM)]
    for i,(name,c) in enumerate(cards):
        yy=y+11+(i%2)*8; xx=x+4+(i//2)*26
        rect(d,xx,yy,23,6,GRID)
        rect(d,xx+2,yy+2,2,2,c)
        text(d,(xx+5,yy+1),name,F(4),INK)

def draw_scene(frame):
    im=Image.new("RGB",(W,H),BG)
    d=ImageDraw.Draw(im)

    # floor / subtle grid
    rect(d,0,112,W,1,GRID)
    for x in range(8,W,24):
        rect(d,x,116,1,13,(19,21,20))
    for y in (120,126,132):
        rect(d,0,y,W,1,(15,17,16))

    # tiny header
    text(d,(9,7),"VEDANT / DIGITAL WORKSPACE",B(7),INK)
    text(d,(9,16),"developer · designer · builder",F(5),DIM)

    # room props
    rect(d,212,30,18,1,DIM)
    rect(d,213,31,16,17,PANEL)
    text(d,(216,35),"OS",B(5),GREEN)
    text(d,(216,42),"LIVE",F(4),DIM)

    # scene stays spatially coherent while character moves.
    desk(d)
    chair(d,143,95)
    terminal(d,77,69, min(1, max(0, (frame-48)/18)))
    project_board(d,16,69, min(1, max(0, (frame-65)/18)))

    # little plant
    rect(d,219,86,2,17,DIM)
    rect(d,214,84,7,3,GREEN)
    rect(d,220,79,5,3,GREEN)
    rect(d,214,102,12,4,DIM)

    # animation timeline:
    # walk in -> sit -> work -> stand/wave -> loop.
    t=(frame % FRAMES)/(FRAMES-1)
    if t < .28:
        q=t/.28
        x=10+int(112*q)
        person_y=98-int(2*math.sin(q*math.pi))
        person(d,x,person_y,"walk",frame)
    elif t < .46:
        q=(t-.28)/.18
        x=122+int(18*q)
        person(d,x,101,"sit",frame)
        # chair appears behind
    elif t < .76:
        q=(t-.46)/.30
        person(d,133,101,"work",frame)
        # screen activity pulses
        pulse=1 if frame%6<3 else 0
        rect(d,166,79,2+pulse,1,GREEN)
        rect(d,171,83,3,1,GREEN)
    elif t < .88:
        q=(t-.76)/.12
        person(d,133-int(22*q),98-int(2*q),"walk",frame)
    else:
        q=(t-.88)/.12
        person(d,109-int(5*q),98,"wave",frame)
        rect(d,122,72,38,12,PANEL)
        rect(d,124,74,34,8,INK)
        text(d,(128,76),"hello.",B(5),BG)

    # bottom status strip
    status="WALKING"
    if .28 <= t < .46: status="AT DESK"
    elif .46 <= t < .76: status="BUILDING"
    elif .76 <= t < .88: status="DONE FOR NOW"
    else: status="HELLO"
    text(d,(183,121),status,B(5),GREEN)

    # scanline-like pixel separators, extremely subtle
    for y in range(0,H,8):
        rect(d,0,y,W,1,(11,12,12))
    return im.resize((W*S,H*S),Image.Resampling.NEAREST)

frames=[draw_scene(i) for i in range(FRAMES)]
os.makedirs("assets",exist_ok=True)
frames[0].save(
    "assets/profile.gif",
    save_all=True,
    append_images=frames[1:],
    duration=105,
    loop=0,
    optimize=True,
    disposal=2,
)
print("wrote assets/profile.gif", os.path.getsize("assets/profile.gif"))
