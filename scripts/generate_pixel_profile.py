from PIL import Image, ImageDraw, ImageFont
import math, os

# Hand-drawn stickman / doodle animation for Vedant's GitHub profile.
# The character physically interacts with the objects: walks, sits, types,
# grabs coffee, drags a chart, opens a browser and ships a project.
# No external artwork; everything is drawn from simple primitives.

W, H = 360, 200
FRAMES = 96
DURATION = 80

BG = (250, 248, 241)
INK = (24, 25, 23)
PAPER = (255, 254, 249)
MUTED = (120, 120, 112)
GREEN = (92, 145, 82)
BLUE = (82, 119, 161)
RED = (181, 82, 73)
YELLOW = (205, 166, 69)
PURPLE = (133, 105, 151)
SKIN = (224, 181, 139)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F = lambda n: ImageFont.truetype(FONT, n)
B = lambda n: ImageFont.truetype(BOLD, n)

def line(d, pts, c=INK, width=2):
    d.line([(int(x), int(y)) for x, y in pts], fill=c, width=width, joint="curve")

def rect(d, x, y, w, h, fill=None, outline=INK, width=2):
    d.rounded_rectangle((int(x), int(y), int(x+w), int(y+h)), radius=3, fill=fill, outline=outline, width=width)

def txt(d, xy, s, font, c=INK):
    d.text((int(xy[0]), int(xy[1])), s, font=font, fill=c)

def ease(x):
    x = max(0.0, min(1.0, x))
    return x*x*(3-2*x)

def lerp(a, b, t):
    return a + (b-a)*ease(t)

def squiggle(d, x, y, length, c=INK, amp=3, phase=0):
    pts=[]
    for i in range(max(3, int(length/4))):
        xx=x+i*4
        yy=y+math.sin(i*.9+phase)*amp
        pts.append((xx,yy))
    line(d, pts, c, 2)

def arrow(d, a, b, c=INK, width=2):
    line(d,[a,b],c,width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for off in (2.55,-2.55):
        p=(b[0]+math.cos(ang+off)*8,b[1]+math.sin(ang+off)*8)
        line(d,[b,p],c,width)

def sticker(d, x, y, w, h, label, accent, phase=0):
    wob=math.sin(phase)*2
    x+=wob
    rect(d,x+3,y+3,w,h,fill=INK,outline=INK,width=2)
    rect(d,x,y,w,h,fill=PAPER,outline=INK,width=2)
    squiggle(d,x+7,y+h-5,w-14,accent,1.2,phase)
    txt(d,(x+7,y+5),label,B(9),INK)

def star(d,x,y,r,c,phase=0):
    r *= .75+.25*(math.sin(phase)+1)/2
    for a in (0,math.pi/2,math.pi/4,-math.pi/4):
        line(d,[(x-math.cos(a)*r,y-math.sin(a)*r),(x+math.cos(a)*r,y+math.sin(a)*r)],c,2)

def stickman(d, x, ground, pose, frame, holding=None):
    # Head
    head_y=ground-48
    d.ellipse((x-11,head_y-11,x+11,head_y+11),outline=INK,width=2,fill=PAPER)
    # tiny expressive face
    if pose=="happy":
        d.arc((x-5,head_y-1,x+5,head_y+7),0,180,fill=INK,width=1)
    else:
        d.ellipse((x-5,head_y-2,x-3,head_y),fill=INK)
        d.ellipse((x+3,head_y-2,x+5,head_y),fill=INK)

    # torso
    neck=(x,head_y+11)
    hip=(x,ground-18)
    line(d,[neck,hip],INK,3)

    if pose=="sit":
        # thighs extend forward, lower legs down
        line(d,[hip,(x+18,ground-12),(x+27,ground-1)],INK,3)
        line(d,[hip,(x+8,ground-8),(x+18,ground-1)],INK,3)
        # arms toward desk
        line(d,[x,ground-37,(x+16),ground-29,(x+29),ground-29],INK,3)
        line(d,[x,ground-37,(x+10),ground-27,(x+24),ground-27],INK,3)
    elif pose=="type":
        tap=2 if (frame//3)%2==0 else 0
        line(d,[x,ground-37,x+16,ground-28,x+31,ground-28+tap],INK,3)
        line(d,[x,ground-37,x+10,ground-27,x+25,ground-27-tap],INK,3)
        line(d,[hip,x-10,ground-2],INK,3)
        line(d,[hip,x+5,ground-1],INK,3)
    elif pose=="drink":
        # one arm bends up to cup
        line(d,[x,ground-37,x+14,ground-29,x+15,ground-43],INK,3)
        line(d,[x,ground-37,x-15,ground-27,x-22,ground-20],INK,3)
        line(d,[hip,x-9,ground-1],INK,3)
        line(d,[hip,x+8,ground-1],INK,3)
    elif pose=="pull":
        line(d,[x,ground-37,x+18,ground-31,x+35,ground-31],INK,3)
        line(d,[x,ground-37,x+17,ground-24,x+35,ground-24],INK,3)
        line(d,[hip,x-12,ground-1],INK,3)
        line(d,[hip,x+9,ground-1],INK,3)
    elif pose=="point":
        line(d,[x,ground-37,x+16,ground-29,x+37,ground-42],INK,3)
        line(d,[x,ground-37,x+15,ground-27,x+29,ground-28],INK,3)
        line(d,[hip,x-10,ground-1],INK,3)
        line(d,[hip,x+9,ground-1],INK,3)
    elif pose=="wave":
        lift=math.sin(frame*.6)*2
        line(d,[x,ground-37,x-15,ground-27,x-20,ground-17],INK,3)
        line(d,[x,ground-37,x+12,ground-25,x+14,ground-45+lift],INK,3)
        line(d,[hip,x-10,ground-1],INK,3)
        line(d,[hip,x+9,ground-1],INK,3)
    else:
        step=5 if (frame//4)%2 else -5
        line(d,[x,ground-37,x-13,ground-26,x-17,ground-17],INK,3)
        line(d,[x,ground-37,x+13,ground-26,x+18,ground-17],INK,3)
        line(d,[hip,x-8+step,ground-1],INK,3)
        line(d,[hip,x+8-step,ground-1],INK,3)

    if holding:
        d.ellipse((holding[0]-4,holding[1]-4,holding[0]+4,holding[1]+4),fill=YELLOW,outline=INK,width=2)

def laptop(d,x,y,frame,open=True):
    # large hand-drawn laptop
    rect(d,x,y,82,48,fill=PAPER,outline=INK,width=3)
    rect(d,x+6,y+6,70,34,fill=(245,246,238),outline=INK,width=2)
    txt(d,(x+10,y+9),"~/vedant",B(8),MUTED)
    code_y=y+21
    for i in range(4):
        w=18+((frame+i*2)%9)
        rect(d,x+10,code_y+i*5,w,2,fill=(GREEN if i==2 else INK),outline=None,width=0)
    # cursor visibly moves as the character types
    cx=x+11+(frame*3)%62
    cy=y+20+((frame//6)%4)*5
    rect(d,cx,cy,3,4,fill=RED,outline=None,width=0)
    # base
    line(d,[(x-7,y+51),(x+89,y+51)],INK,4)
    line(d,[(x+24,y+51),(x+64,y+51)],MUTED,2)

def coffee(d,x,y,frame):
    rect(d,x,y,15,11,fill=YELLOW,outline=INK,width=2)
    line(d,[(x+15,y+3),(x+21,y+3),(x+21,y+9),(x+15,y+9)],INK,2)
    for i in range(2):
        xx=x+4+i*6
        yy=y-3-int((frame+i*8)%18)
        line(d,[(xx,yy+5),(xx-2,yy+2),(xx+1,yy)],MUTED,1)

def browser(d,x,y,frame):
    slide=math.sin(frame*.13)*4
    x+=slide
    rect(d,x,y,92,53,fill=PAPER,outline=INK,width=3)
    line(d,[(x,y+13),(x+92,y+13)],INK,2)
    for i,c in enumerate((RED,YELLOW,GREEN)):
        d.ellipse((x+7+i*8,y+4,x+12+i*8,y+9),fill=c,outline=INK,width=1)
    txt(d,(x+8,y+19),"buildbybits.dev",B(8),INK)
    for i in range(3):
        ww=42+int(8*math.sin(frame*.2+i))
        line(d,[(x+9,y+33+i*6),(x+9+ww,y+33+i*6)],GREEN if i==1 else MUTED,2)

def graph(d,x,y,frame,drag=0):
    rect(d,x,y,72,48,fill=PAPER,outline=INK,width=2)
    txt(d,(x+7,y+6),"ACTIVITY",B(7),INK)
    pts=[]
    for i in range(8):
        xx=x+8+i*7
        yy=y+36-10*math.sin(i*.75+frame*.06)-3*math.sin(i)
        pts.append((xx+drag,yy))
    line(d,pts,BLUE,3)
    for px,py in pts[::2]:
        d.ellipse((px-2,py-2,px+2,py+2),fill=RED,outline=INK,width=1)

def desk(d,frame):
    # desk and plant are alive too
    y=144+int(math.sin(frame*.13))
    line(d,[(142,y),(343,y)],INK,4)
    line(d,[(154,y),(154,190)],MUTED,3)
    line(d,[(327,y),(327,190)],MUTED,3)
    # plant
    sway=math.sin(frame*.16)*4
    line(d,[(310,y),(310+sway,122)],GREEN,3)
    line(d,[(310+sway,128),(299+sway,119)],GREEN,3)
    line(d,[(310+sway,126),(320+sway,115)],GREEN,3)
    d.ellipse((292+sway,112,306+sway,121),fill=GREEN,outline=INK,width=2)
    d.ellipse((316+sway,108,329+sway,118),fill=GREEN,outline=INK,width=2)

def scene(frame):
    im=Image.new("RGB",(W,H),BG)
    d=ImageDraw.Draw(im)

    # paper-like doodle background
    for y in range(18,H,22):
        squiggle(d,0,y,W,(232,230,220),1,frame*.02+y)

    # Title and moving underline
    txt(d,(14,9),"VEDANT",B(28),INK)
    txt(d,(17,42),"developer · designer · builder",F(10),MUTED)
    squiggle(d,17,57,118,GREEN,2,frame*.12)

    # Stickers physically bounce in.
    sticker(d,155,10,66,28,"BUILD",GREEN,frame*.16)
    sticker(d,230,23,73,28,"DESIGN",BLUE,frame*.16+2)
    sticker(d,287,67,58,27,"SHIP",RED,frame*.16+4)

    # Loose doodles
    star(d,145,26,9,YELLOW,frame*.3)
    star(d,337,39,7,PURPLE,frame*.3)
    arrow(d,(131,69),(165,61),BLUE,2)
    squiggle(d,245,93,63,RED,2,frame*.15)

    desk(d,frame)

    # Work objects
    laptop(d,182,94,frame)
    coffee(d,276,125,frame)
    browser(d,18,103,frame)

    # A graph that the stickman will physically drag.
    drag=0
    graph_x=253
    if 58 <= frame < 74:
        q=ease((frame-58)/16)
        drag=22*q
    graph(d,graph_x+drag,94,frame)

    # Main story:
    # 0-17: walk in
    # 18-34: sit and type
    # 35-48: get coffee and drink
    # 49-74: drag graph / open browser
    # 75-95: ship + wave
    if frame < 18:
        q=frame/17
        x=55+int(105*ease(q))
        stickman(d,x,143,"walk",frame)
        txt(d,(35,75),"let's build something",B(10),INK)
    elif frame < 35:
        x=165
        stickman(d,x,143,"type",frame)
        # hands meet keyboard; little keystroke marks appear
        for i in range(4):
            if (frame+i*2)%7 < 3:
                txt(d,(194+i*10,82-i*3),"·",B(10),(GREEN,BLUE,RED,YELLOW)[i])
        txt(d,(183,72),"typing...",B(8),MUTED)
    elif frame < 49:
        q=ease((frame-35)/14)
        x=int(165-34*q)
        if q < .45:
            stickman(d,x,143,"walk",frame)
        else:
            stickman(d,x,143,"drink",frame,holding=(276,125))
        if q > .45:
            coffee(d,276,125,frame)
            txt(d,(225,73),"coffee break",B(8),MUTED)
    elif frame < 58:
        x=int(131+34*ease((frame-49)/9))
        stickman(d,x,143,"walk",frame)
        arrow(d,(156,115),(253,110),PURPLE,2)
        txt(d,(177,73),"check the numbers",B(8),MUTED)
    elif frame < 75:
        q=ease((frame-58)/17)
        x=int(165+22*q)
        stickman(d,x,143,"pull",frame)
        # Character's hands hold the chart edge while it moves.
        arrow(d,(206,115),(253+int(22*q),110),BLUE,2)
        txt(d,(205,73),"drag →",B(8),BLUE)
    elif frame < 84:
        x=187
        stickman(d,x,143,"point",frame)
        txt(d,(219,73),"ship it.",B(10),GREEN)
        sticker(d,258,55,66,28,"SHIPPED",GREEN,frame*.25)
        for i in range(5):
            star(d,230+i*20,84-int(5*math.sin(frame+i)),4,(GREEN,BLUE,RED,YELLOW,PURPLE)[i],frame+i)
    else:
        q=(frame-84)/11
        x=205
        stickman(d,x,143,"wave",frame)
        txt(d,(225,73),"see you next loop",B(9),INK)
        sticker(d,90,69,72,28,"AGAIN",YELLOW,frame*.18)
        arrow(d,(163,82),(196,91),RED,2)

    # Animated little cursor follows the action.
    cx=35+((frame*5)%285)
    cy=62+10*math.sin(frame*.23)
    line(d,[(cx,cy),(cx+8,cy+3)],INK,2)
    line(d,[(cx+8,cy+3),(cx+4,cy+8)],INK,2)

    # Footer
    txt(d,(16,181),"software · product · AI · automation · creative technology",F(8),MUTED)
    line(d,[(16,194),(344,194)],INK,2)
    progress=frame/(FRAMES-1)
    line(d,[(16,194),(16+328*progress,194)],GREEN,4)

    return im

frames=[scene(i) for i in range(FRAMES)]
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
