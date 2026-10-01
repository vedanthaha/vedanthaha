from PIL import Image, ImageDraw, ImageFont
import urllib.request, json, datetime, os, math, time

REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(path,size): return ImageFont.truetype(path,size)

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"vedanthaha-profile-visuals"})
    with urllib.request.urlopen(req,timeout=20) as r:
        return json.loads(r.read().decode())

REPO="vedanthaha/vedanthaha"

# ---------- REAL GITHUB DATA ----------
weeks=[]
try:
    data=get_json(f"https://api.github.com/repos/{REPO}/stats/commit_activity")
    if isinstance(data,list) and data:
        weeks=data[-12:]
except Exception:
    weeks=[]

if not weeks:
    # Only a rendering fallback; normally Actions receives live GitHub data.
    now=int(time.time())
    weeks=[{"week":now-(11-i)*604800,"total":0} for i in range(12)]

try:
    langs=get_json(f"https://api.github.com/repos/{REPO}/languages")
except Exception:
    langs={}
total_lang=sum(langs.values()) or 1
lang_rows=sorted(langs.items(),key=lambda x:x[1],reverse=True)[:6]
lang_rows=[(k,v/total_lang*100) for k,v in lang_rows]

# ---------- CLEAR EDITORIAL DATA GIF ----------
W,H,FRAMES=1000,650,48
bg=(241,240,235); ink=(28,28,26); muted=(133,131,124); grid=(218,216,209)
frames=[]
commits=[int(w.get("total",0)) for w in weeks]
labels=[]
for w in weeks:
    dt=datetime.datetime.fromtimestamp(w["week"],datetime.timezone.utc)
    labels.append(dt.strftime("%b").upper())

for fi in range(FRAMES):
    im=Image.new("RGB",(W,H),bg); d=ImageDraw.Draw(im)
    d.rounded_rectangle((5,5,W-5,H-5),20,outline=(213,211,204),width=1)

    # CHART 1: actual weekly commit activity
    d.text((36,30),"NINETY DAYS AS A BARCODE",font=font(BOLD,17),fill=ink)
    d.text((36,53),"real GitHub commit activity · updated by Actions",font=font(REG,10),fill=muted)
    x0,y0=55,105; cw=890; ch=205
    d.line((x0,y0+ch,x0+cw,y0+ch),fill=grid,width=2)
    maxv=max(commits+[1])
    barw=48
    for i,v in enumerate(commits):
        x=x0+i*72+8
        phase=(fi/FRAMES)*math.pi*2
        # Animate reveal + a subtle pulse, while preserving the real value.
        reveal=min(1,max(0,(fi-i*2)/12))
        h=(v/maxv)*ch*reveal
        # light vertical range
        d.line((x,y0+ch,x,y0+ch-h),fill=(197,195,188),width=2)
        d.ellipse((x-5,y0+ch-h-5,x+5,y0+ch-h+5),fill=ink)
        if v:
            d.text((x-7,y0+ch-h-23),str(v),font=font(BOLD,10),fill=ink)
        d.text((x-12,y0+ch+14),labels[i],font=font(REG,9),fill=muted)
    d.text((36,325),f"TOTAL COMMITS  {sum(commits)}",font=font(BOLD,11),fill=ink)
    d.text((210,325),"weekly values are pulled from GitHub, not hand-authored",font=font(REG,9),fill=muted)

    # CHART 2: actual language share
    px,py,pw,ph=36,365,928,235
    d.rounded_rectangle((px,py,px+pw,py+ph),14,fill=(29,29,27))
    d.text((58,389),"SOFTWARE DNA",font=font(BOLD,16),fill=(244,243,238))
    d.text((58,412),"repository language distribution · actual GitHub bytes",font=font(REG,9),fill=(151,149,143))
    left=58; base=550; maxh=108
    for i,(name,pct) in enumerate(lang_rows):
        x=left+i*140
        target_h=maxh*pct/100
        reveal=min(1,max(0,(fi-i*2)/14))
        h=target_h*reveal
        d.rounded_rectangle((x,base-h,x+78,base),12,fill=(228,227,221) if i==0 else (148,147,142))
        d.text((x,565),name.upper()[:11],font=font(BOLD,9),fill=(210,209,203))
        d.text((x,base-h-22),f"{pct:.0f}%",font=font(BOLD,10),fill=(244,243,238))
    d.text((58,590),"source: github.com/vedanthaha/vedanthaha",font=font(REG,8),fill=(108,106,101))
    frames.append(im)

im0=frames[0]
im0.save("assets/project-software.gif",save_all=True,append_images=frames[1:],duration=90,loop=0,optimize=True,disposal=2)

# ---------- PIXEL DAY: WALK → SIT → WORK → WAVE ----------
S=6
LW,LH=150,58
W,H=900,348
frames=[]
palette={"bg":(14,14,14),"floor":(47,47,45),"white":(235,235,228),"gray":(103,103,98),
         "dark":(26,26,24),"skin":(219,181,143),"hair":(42,35,30),"shirt":(196,196,188),
         "pants":(79,79,76),"accent":(145,145,138),"green":(83,105,77)}

def pxrect(d,x,y,w,h,c): d.rectangle((x*S,y*S,(x+w)*S-1,(y+h)*S-1),fill=c)

for fi in range(72):
    im=Image.new("RGB",(LW*S,LH*S),palette["bg"]); d=ImageDraw.Draw(im)

    # room
    pxrect(d,0,48,150,1,palette["floor"])
    # plant
    pxrect(d,128,34,2,14,palette["gray"]); pxrect(d,125,29,7,4,palette["green"]); pxrect(d,129,26,6,4,palette["green"])
    pxrect(d,126,46,7,3,palette["accent"])

    # desk + laptop
    pxrect(d,91,37,32,2,palette["white"]); pxrect(d,94,39,2,9,palette["gray"]); pxrect(d,119,39,2,9,palette["gray"])
    pxrect(d,102,30,12,7,palette["gray"]); pxrect(d,103,31,10,5,palette["dark"])
    pxrect(d,100,37,17,2,palette["white"])

    phase=fi/71
    # phases: walk 0-.28, sit .28-.55, work .55-.82, wave .82-1
    if phase < .28:
        q=phase/.28
        x=12+int(72*q)
        y=36-int(3*math.sin(q*math.pi))
        pose="walk"
    elif phase < .55:
        q=(phase-.28)/.27
        x=84+int(7*q); y=36+int(6*q)
        pose="sit"
    elif phase < .82:
        q=(phase-.55)/.27
        x=91; y=41
        pose="work"
    else:
        q=(phase-.82)/.18
        x=91-int(34*q); y=35-int(3*math.sin(q*math.pi))
        pose="wave"

    # character, all pixel primitives
    # head
    pxrect(d,x+3,y-14,7,7,palette["skin"]); pxrect(d,x+3,y-15,7,2,palette["hair"])
    pxrect(d,x+2,y-14,2,4,palette["hair"]); pxrect(d,x+9,y-13,1,2,palette["hair"])
    # torso
    pxrect(d,x+1,y-7,11,12,palette["shirt"])
    # legs
    if pose=="sit" or pose=="work":
        pxrect(d,x+2,y+5,5,7,palette["pants"]); pxrect(d,x+8,y+5,5,4,palette["pants"])
        pxrect(d,x+8,y+8,8,3,palette["pants"])
    else:
        step=(-1 if fi%8<4 else 1)
        pxrect(d,x+2,y+5,4,9,palette["pants"])
        pxrect(d,x+8,y+5,4,8,palette["pants"])
        pxrect(d,x+1+step,y+13,6,2,palette["white"]); pxrect(d,x+7-step,y+13,6,2,palette["white"])
    # arms
    if pose=="work":
        pxrect(d,x+10,y-5,8,3,palette["shirt"]); pxrect(d,x+16,y-3,4,2,palette["skin"])
        pxrect(d,x+1,y-5,6,3,palette["shirt"]); pxrect(d,x-2,y-3,4,2,palette["skin"])
    elif pose=="wave":
        wave=int(2*math.sin(q*math.pi*4))
        pxrect(d,x+10,y-5,3,3,palette["shirt"]); pxrect(d,x+12,y-9-wave,3,5,palette["skin"])
        pxrect(d,x+13,y-12-wave,2,3,palette["skin"])
        pxrect(d,x+1,y-5,5,3,palette["shirt"]); pxrect(d,x-3,y-3,4,2,palette["skin"])
    else:
        pxrect(d,x-2,y-5,5,3,palette["shirt"]); pxrect(d,x-4,y-3,4,2,palette["skin"])
        pxrect(d,x+10,y-5,5,3,palette["shirt"]); pxrect(d,x+14,y-3,4,2,palette["skin"])

    # speech during wave + work label
    if pose=="wave":
        pxrect(d,99,10,42,12,palette["dark"]); pxrect(d,101,12,38,8,palette["white"])
        d.text((612,74),"hello :)",font=font(BOLD,15),fill=palette["dark"])
    elif pose=="work":
        d.text((525,74),"shipping...",font=font(BOLD,13),fill=palette["white"])

    # upscale is already pixelated because every primitive is SxS
    frames.append(im)

frames[0].save("assets/pixel-hello.gif",save_all=True,append_images=frames[1:],duration=100,loop=0,optimize=True,disposal=2)
print("updated real-data chart + pixel day animation")
