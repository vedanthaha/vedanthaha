from PIL import Image, ImageDraw, ImageFont
import math, os

# Motion-graphics doodle / sticker profile.
# Everything moves: type, stickers, charts, cursor, windows, props, character, sparks.
# Hand-authored primitives only — no generated artwork or external assets.

S = 4
W, H = 240, 135
FRAMES = 120
DURATION = 75

BG = (10, 11, 11)
PAPER = (235, 233, 220)
INK = (22, 23, 22)
MUTED = (115, 116, 108)
GRID = (34, 36, 34)
GREEN = (139, 183, 116)
BLUE = (117, 151, 185)
RED = (203, 116, 104)
YELLOW = (218, 190, 105)
PURPLE = (157, 133, 178)
SKIN = (213, 173, 134)
HAIR = (49, 39, 34)
SHIRT = (220, 219, 207)
PANTS = (77, 79, 76)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F = lambda n: ImageFont.truetype(FONT, n)
B = lambda n: ImageFont.truetype(BOLD, n)

def rect(d, x, y, w, h, c):
    d.rectangle((int(x), int(y), int(x+w-1), int(y+h-1)), fill=c)

def line(d, pts, c, width=1):
    d.line([(int(x), int(y)) for x,y in pts], fill=c, width=width)

def txt(d, xy, s, font, c):
    d.text((int(xy[0]), int(xy[1])), s, font=font, fill=c)

def ease(x):
    x = max(0, min(1, x))
    return x*x*(3-2*x)

def pulse(frame, speed=1.0, phase=0.0):
    return (math.sin(frame*speed + phase) + 1) / 2

def sticker(d, x, y, w, h, label, accent, tilt=0, phase=0):
    # A chunky outlined sticker with a tiny animated wobble.
    wob = math.sin(phase)*1.1
    x += wob
    rect(d, x+1, y+2, w, h, INK)
    rect(d, x, y, w, h, PAPER)
    rect(d, x+2, y+2, w-4, h-4, PAPER)
    line(d, [(x+2,y+h-3),(x+w-4,y+h-3)], accent)
    txt(d, (x+5,y+4), label, B(5), INK)

def arrow(d, pts, c, width=1, head=4):
    line(d, pts, c, width)
    x1,y1 = pts[-2]; x2,y2 = pts[-1]
    ang = math.atan2(y2-y1,x2-x1)
    a1 = ang + 2.5
    a2 = ang - 2.5
    line(d, [(x2,y2),(x2+math.cos(a1)*head,y2+math.sin(a1)*head)], c, width)
    line(d, [(x2,y2),(x2+math.cos(a2)*head,y2+math.sin(a2)*head)], c, width)

def star(d, x, y, r, c, phase):
    k = 0.55 + 0.45*pulse(phase, .28)
    r *= k
    line(d, [(x-r,y),(x+r,y)], c)
    line(d, [(x,y-r),(x,y+r)], c)
    line(d, [(x-r*.65,y-r*.65),(x+r*.65,y+r*.65)], c)
    line(d, [(x-r*.65,y+r*.65),(x+r*.65,y-r*.65)], c)

def doodle_circle(d, x, y, r, c, phase):
    # deliberately imperfect multi-stroke circle
    pts=[]
    for i in range(25):
        a=2*math.pi*i/24
        rr=r + .8*math.sin(i*2.3+phase)
        pts.append((x+math.cos(a)*rr,y+math.sin(a)*rr))
    line(d, pts+[pts[0]], c)

def character(d, x, y, state, frame):
    # sticker-like pixel doodle character
    bob = int(round(1.0*math.sin(frame*.45))) if state in ("walk","work") else 0
    y += bob

    # shadow
    shadow = 1 + int(1*pulse(frame,.3))
    rect(d,x+1,y+14,16,shadow,GRID)

    # head / hair
    rect(d,x+4,y-16,9,8,SKIN)
    rect(d,x+4,y-17,9,3,HAIR)
    rect(d,x+3,y-16,2,4,HAIR)
    rect(d,x+12,y-15,2,3,HAIR)

    # body
    rect(d,x+3,y-8,11,12,SHIRT)

    if state == "sit":
        rect(d,x+4,y+3,5,7,PANTS)
        rect(d,x+9,y+3,5,5,PANTS)
        rect(d,x+11,y+7,7,3,PANTS)
        rect(d,x-1,y-6,6,3,SHIRT)
        rect(d,x-3,y-4,3,2,SKIN)
        rect(d,x+12,y-6,5,3,SHIRT)
        rect(d,x+16,y-4,3,2,SKIN)
    elif state == "work":
        # arms repeatedly type
        tap = 1 if frame % 6 < 3 else 0
        rect(d,x-1,y-6,6,3,SHIRT)
        rect(d,x-3,y-4,3,2,SKIN)
        rect(d,x+12,y-6+tap,7,3,SHIRT)
        rect(d,x+18,y-4+tap,3,2,SKIN)
        rect(d,x+4,y+3,5,9,PANTS)
        rect(d,x+9,y+3,5,9,PANTS)
        rect(d,x+2,y+11,7,2,INK)
        rect(d,x+9,y+11,7,2,INK)
    elif state == "wave":
        rect(d,x-1,y-6,6,3,SHIRT)
        rect(d,x-3,y-4,3,2,SKIN)
        lift = int(round(2*math.sin(frame*.8)))
        rect(d,x+12,y-8,4,4,SHIRT)
        rect(d,x+14,y-13-lift,3,6,SKIN)
        rect(d,x+15,y-16-lift,2,3,SKIN)
        rect(d,x+4,y+3,5,9,PANTS)
        rect(d,x+9,y+3,5,9,PANTS)
        rect(d,x+2,y+11,7,2,INK)
        rect(d,x+9,y+11,7,2,INK)
    else:
        step = -2 if frame % 8 < 4 else 2
        rect(d,x+4,y+3,4,9,PANTS)
        rect(d,x+10,y+3,4,9,PANTS)
        rect(d,x+2+step,y+11,6,2,INK)
        rect(d,x+9-step,y+11,6,2,INK)
        rect(d,x-1,y-6,5,3,SHIRT)
        rect(d,x-3,y-4,3,2,SKIN)
        rect(d,x+13,y-6,5,3,SHIRT)
        rect(d,x+17,y-4,3,2,SKIN)

def laptop(d, x, y, frame, active=True):
    # animated screen + keyboard + cursor
    rect(d,x,y,28,13,INK)
    rect(d,x+2,y+2,24,9,PAPER)
    # fake code lines
    for i,w in enumerate((8,14,10,18)):
        ww = w + (1 if frame%8 < 4 and i==1 else 0)
        rect(d,x+4,y+4+i*1.6,ww,1, GREEN if i in (0,3) else INK)
    if active:
        cx=x+5+(frame*2)%17
        cy=y+4+(frame//10)%5
        rect(d,cx,cy,2,2,RED)
    rect(d,x-2,y+13,32,2,PAPER)
    rect(d,x+9,y+13,12,1,INK)

def coffee(d, x, y, frame):
    rect(d,x,y,8,6,INK)
    rect(d,x+1,y+1,6,4,YELLOW)
    line(d,[(x+8,y+1),(x+11,y+1),(x+11,y+4),(x+8,y+4)],INK)
    for i in range(2):
        yy = y-2-int((frame+i*7)%18/6)
        xx = x+2+i*3+int(math.sin(frame*.2+i)*1)
        line(d,[(xx,yy+3),(xx-1,yy+1),(xx+1,yy)],MUTED)

def mini_graph(d, x, y, frame):
    # line chart draws on, then breathes.
    rect(d,x,y,48,29,PAPER)
    txt(d,(x+4,y+3),"ACTIVITY",B(5),INK)
    pts=[]
    n=12
    visible=min(n, max(1, int((frame%50)/4)+1))
    for i in range(visible):
        xx=x+5+i*3.2
        yy=y+22-4*math.sin(i*.9)-3*math.sin(i*.37+frame*.05)
        pts.append((xx,yy))
    if len(pts)>1: line(d,pts,BLUE,2)
    for i in range(0,12,3):
        rect(d,x+5+i*3.2,y+23,1,1,INK)

def browser_window(d, x, y, frame):
    slide = int(8*math.sin(frame*.18))
    x += slide
    rect(d,x+1,y+1,51,31,INK)
    rect(d,x,y,51,31,PAPER)
    rect(d,x+3,y+3,45,4,GRID)
    for i,c in enumerate((RED,YELLOW,GREEN)):
        rect(d,x+5+i*4,y+4,2,2,c)
    txt(d,(x+5,y+10),"buildbybits.dev",B(5),INK)
    # page blocks animate like a design-tool prototype
    for i in range(3):
        w=18 + int(5*pulse(frame+i*4,.16))
        rect(d,x+5,y+17+i*4,w,2, GREEN if i==1 else MUTED)

def terminal(d, x, y, frame):
    rect(d,x,y,52,30,INK)
    rect(d,x+1,y+1,50,28,BG)
    txt(d,(x+4,y+4),"~/vedant",B(5),PAPER)
    lines=["> npm run build","> compiling","> ui ready","> ship --now"]
    for i,s in enumerate(lines):
        reveal=int(max(0,min(len(s), (frame-i*5)%48)))
        txt(d,(x+4,y+10+i*4),s[:reveal],F(4),GREEN if i==3 else PAPER)

def desk_scene(d, frame):
    # Desk itself gently shifts like a hand-animated sticker.
    j = int(round(math.sin(frame*.22)*.5))
    rect(d,145,92+j,55,3,INK)
    rect(d,148,95+j,3,27,MUTED)
    rect(d,194,95+j,3,27,MUTED)
    laptop(d,160,77+j,frame)
    coffee(d,181,85+j,frame)

def draw_scene(frame):
    im=Image.new("RGB",(W,H),BG)
    d=ImageDraw.Draw(im)

    # moving doodle grid / paper texture
    drift=(frame//4)%12
    for x in range(-12, W+12, 24):
        xx=x+drift
        line(d,[(xx,0),(xx-5,H)],(18,20,19))
    for y in range(8,H,12):
        line(d,[(0,y+int(math.sin(frame*.1+y)*.5)),(W,y)],(15,17,16))

    # header is a moving sticker lockup
    title_x=8+int(2*math.sin(frame*.12))
    txt(d,(title_x,6),"VEDANT",B(12),PAPER)
    txt(d,(10,20),"developer / designer / builder",F(5),MUTED)
    line(d,[(10,28),(82+int(4*pulse(frame,.13)),28)],GREEN,2)

    # floating stickers orbit around the composition
    sticker(d,91,7,43,15,"BUILD",GREEN,0,frame*.25)
    sticker(d,148,10,42,15,"DESIGN",BLUE,0,frame*.25+2)
    sticker(d,196,18,35,15,"SHIP",RED,0,frame*.25+4)

    # playful doodles animate continuously
    doodle_circle(d,219,55,9,MUTED,frame*.2)
    star(d,204+int(2*math.sin(frame*.2)),45,4,YELLOW,frame)
    star(d,17,44,3,GREEN,frame+5)
    arrow(d,84,46,111,37,BLUE)
    arrow(d,73,59,95,54,GREEN)

    # floating idea bubble / callout
    bx=86+int(3*math.sin(frame*.15))
    rect(d,bx,31,62,12,PAPER)
    txt(d,(bx+5,34),"make → move → ship",B(5),INK)
    line(d,[(bx+15,43),(bx+11,48)],PAPER)
    line(d,[(bx+15,43),(bx+18,47)],PAPER)

    # windows / work objects slide, pulse and redraw
    browser_window(d,10,72,frame)
    terminal(d,67,73,frame)
    mini_graph(d,202,69,frame+8)

    # tiny side notes
    txt(d,(12,107),"AI",B(5),GREEN)
    txt(d,(27,107),"WEB",B(5),BLUE)
    txt(d,(47,107),"MOTION",B(5),RED)
    txt(d,(76,107),"AUTOMATION",B(5),YELLOW)

    # desk + plant
    desk_scene(d,frame)
    rect(d,216,94,9,12,INK)
    rect(d,218,90,5,5,GREEN)
    rect(d,214,92,5,4,GREEN)
    rect(d,220,87,4,5,GREEN)
    # plant sway
    sway=int(round(math.sin(frame*.18)*2))
    line(d,[(220,94),(220+sway,87)],GREEN,1)
    line(d,[(220,92),(216+sway,89)],GREEN,1)

    # character timeline: run in -> bounce -> sit -> work -> explode into doodles -> wave
    t=(frame%FRAMES)/(FRAMES-1)
    if t < .18:
        q=ease(t/.18)
        x=-8+int(113*q)
        character(d,x,101,"walk",frame)
    elif t < .30:
        q=ease((t-.18)/.12)
        character(d,105+int(24*q),101,"walk",frame)
        # landing/sit impact lines
        if q>.45:
            line(d,[(128,111),(125,114)],PAPER)
            line(d,[(128,111),(132,114)],PAPER)
    elif t < .66:
        q=(t-.30)/.36
        character(d,132,101,"work",frame)
        # keyboard particles + cursor clicks
        for i in range(4):
            if (frame+i*3)%13 < 6:
                px=150+i*6
                py=72-i*3-int(2*pulse(frame+i,.3))
                rect(d,px,py,2,1,(GREEN,BLUE,RED,YELLOW)[i])
        if frame%18 in range(0,5):
            star(d,157+(frame%3),67,2,GREEN,frame)
    elif t < .78:
        q=ease((t-.66)/.12)
        character(d,132-int(30*q),101-int(4*q),"walk",frame)
        # "work done" sticker flies upward
        sy=64-int(18*q)
        sticker(d,112,sy,45,14,"SHIPPED",GREEN,0,frame*.3)
    else:
        q=(t-.78)/.22
        character(d,102,101,"wave",frame)
        # end-card doodles orbit and scale
        rr=10+int(3*pulse(frame,.25))
        doodle_circle(d,111,83,rr,GREEN,frame*.2)
        txt(d,(117,78),"hey.",B(7),PAPER)
        sticker(d,78,94,39,14,"HELLO",YELLOW,0,frame*.3)
        sticker(d,137,95,39,14,"AGAIN",BLUE,0,frame*.3+2)
        arrow(d,103,61,95,55,RED)

    # Footer timeline ticks — animated progress bar
    progress=(frame%FRAMES)/(FRAMES-1)
    line(d,[(8,129),(232,129)],GRID,2)
    line(d,[(8,129),(8+224*progress,129)],GREEN,2)
    rect(d,8+224*progress,127,3,5,PAPER)

    # frame marker / live label
    txt(d,(193,119),"LIVE / LOOP",B(4),GREEN)

    # sparse animated ink flecks
    for i in range(7):
        xx=(31+i*37+frame*(i%3+1))%236
        yy=(35+i*11+(frame//4)*(i+1))%88
        rect(d,xx,yy,1+(i%2),1,(MUTED if i%2 else GRID))

    return im.resize((W*S,H*S),Image.Resampling.NEAREST)

frames=[draw_scene(i) for i in range(FRAMES)]
os.makedirs("assets",exist_ok=True)
frames[0].save(
    "assets/profile.gif",
    save_all=True,
    append_images=frames[1:],
    duration=DURATION,
    loop=0,
    optimize=True,
    disposal=2,
)
print("wrote assets/profile.gif", os.path.getsize("assets/profile.gif"))
