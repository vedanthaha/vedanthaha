from PIL import Image, ImageDraw, ImageFont
import math, os

REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def F(path,size): return ImageFont.truetype(path,size)

os.makedirs("assets", exist_ok=True)

# Editorial project/software chart inspired by the supplied reference.
W,H,FRAMES=900,570,48
bg=(242,241,236); ink=(27,27,25); muted=(135,133,126); grid=(224,222,215); black=(28,28,26)
projects=["BLINKY","CIVIFIX","DROP","DAILYS","CATCHUP","LYRIX"]
langs=[("TS",8),("JS",7),("PY",6),("SQL",5),("GO",4),("CSS",4),("Svelte",3),("React",3)]
bars=[52,78,64,91,70,84,60,73,88,67,80,58,72,94,76,86,63,77]
frames=[]

for fi in range(FRAMES):
    t=fi/(FRAMES-1); im=Image.new("RGB",(W,H),bg); d=ImageDraw.Draw(im)
    d.rounded_rectangle((6,6,W-6,H-6),22,outline=(216,214,207),width=1)
    d.text((34,25),"PROJECTS / SOFTWARE",font=F(BOLD,16),fill=ink)
    d.text((34,46),"a visual index of what I build and what I build with",font=F(REG,10),fill=muted)

    d.rounded_rectangle((34,72,432,260),14,outline=grid,width=1)
    d.text((52,90),"Six things I keep building",font=F(BOLD,13),fill=ink)
    d.text((52,110),"projects · product · experiments",font=F(REG,9),fill=muted)
    cx,cy,rx,ry=232,222,150,72
    start,end=math.radians(205),math.radians(340)
    pts=[(cx+rx*math.cos(start+(end-start)*k/60),cy+ry*math.sin(start+(end-start)*k/60)) for k in range(61)]
    d.line(pts,fill=grid,width=2)
    reveal=min(1,t*1.3)
    for i,name in enumerate(projects):
        a=start+(end-start)*i/5; px=cx+rx*math.cos(a); py=cy+ry*math.sin(a)
        active=i<reveal*len(projects); r=4+int(1.5*math.sin(fi*.3+i)) if active else 2
        d.ellipse((px-r,py-r,px+r,py+r),fill=ink if active else grid)
        if active: d.text((px-12,py+9),f"{i+1:02d}",font=F(REG,8),fill=muted)
    d.text((52,235),"01   02   03   04   05   06",font=F(REG,8),fill=muted)

    d.rounded_rectangle((452,72,866,260),14,fill=black)
    d.text((470,90),"What the stack looks like",font=F(BOLD,13),fill=(245,244,239))
    d.text((470,110),"languages · frameworks · tools",font=F(REG,9),fill=(150,149,143))
    for i,(lab,val) in enumerate(langs):
        yy=224-i*16; active=int(val*(.45+.55*(.5+.5*math.sin(fi*.13+i*.6))))
        for j in range(val):
            xx=488+j*20+i*1.5; r=2.5 if j<active else 1.7
            d.ellipse((xx-r,yy-r,xx+r,yy+r),fill=(244,243,238) if j<active else (70,69,65))
        d.text((790,yy-5),lab,font=F(REG,8),fill=(155,153,147))

    d.text((52,287),"NINETY DAYS AS A BARCODE",font=F(BOLD,13),fill=ink)
    d.text((52,305),"shipping rhythm · commits · experiments · releases",font=F(REG,9),fill=muted)
    base=360
    for i,v in enumerate(bars):
        x=58+i*42; h=int(v*(.55+.45*math.sin(fi*.12+i*.25)))
        d.line((x,base-h,x,base+8),fill=grid,width=2); d.ellipse((x-3,base-h-3,x+3,base-h+3),fill=ink)
    d.text((52,375),"JAN",font=F(REG,8),fill=muted); d.text((420,375),"JUN",font=F(REG,8),fill=muted); d.text((820,375),"NOW",font=F(REG,8),fill=muted)

    d.text((52,405),"PROJECT SURFACE AREA",font=F(BOLD,12),fill=ink)
    d.text((52,422),"where the work spends its time",font=F(REG,8),fill=muted)
    labels=["UI","APP","DATA","AI","AUTO","MOTION"]; vals=[74,88,58,64,48,72]
    for i,(lab,val) in enumerate(zip(labels,vals)):
        x=70+i*57; bh=val*.8*(.9+.1*math.sin(fi*.2+i))
        d.rounded_rectangle((x,515-bh,x+31,515),7,fill=ink if i==1 else (150,149,144)); d.text((x+2,523),lab,font=F(REG,8),fill=muted)

    d.text((430,405),"SOFTWARE DNA",font=F(BOLD,12),fill=ink)
    d.text((430,422),"a compact view of the tools behind the work",font=F(REG,8),fill=muted)
    for row,(lab,count) in enumerate([("frontend",5),("backend",4),("data",3),("creative",2),("infra",1)]):
        y=458+row*18; d.text((430,y-5),lab,font=F(REG,8),fill=muted)
        for j in range(10):
            xx=512+j*18; on=j<count*2 and math.sin(fi*.18+j*.6+row)>.2; r=3.5 if on else 2
            d.ellipse((xx-r,y-r,xx+r,y+r),fill=ink if on else grid)
    frames.append(im)

frames[0].save("assets/project-software.gif",save_all=True,append_images=frames[1:],duration=80,loop=0,optimize=True,disposal=2)

# Small walking pixel companion.
W,H,FRAMES=900,190,40; frames=[]
for fi in range(FRAMES):
    im=Image.new("RGB",(W,H),(13,13,13)); d=ImageDraw.Draw(im)
    d.line((28,157,872,157),fill=(50,50,50),width=2)
    x=90+int(fi/(FRAMES-1)*690); step=fi%8
    skin=(232,196,158); shirt=(245,245,240); pants=(92,92,92); dark=(18,18,18)
    d.text((30,25),"HELLO FROM THE BUILD SIDE",font=F(BOLD,12),fill=(115,115,110))
    d.rectangle((x-18,153,x+20,157),fill=(35,35,35))
    d.rectangle((x-16,82,x+16,103),fill=dark); d.rectangle((x-11,79,x+12,84),fill=dark)
    d.rectangle((x-9,87,x+13,100),fill=skin); d.rectangle((x+6,90,x+9,93),fill=dark)
    d.rectangle((x-14,105,x+14,136),fill=shirt)
    if step in (1,2,3,4):
        d.rectangle((x+15,107,x+22,124),fill=shirt); d.rectangle((x+20,98,x+27,113),fill=skin); d.rectangle((x+25,89,x+32,102),fill=skin)
    else:
        d.rectangle((x+15,109,x+22,133),fill=shirt); d.rectangle((x+17,130,x+24,140),fill=skin)
    d.rectangle((x-22,109,x-15,132),fill=shirt); d.rectangle((x-24,130,x-17,140),fill=skin)
    if step%2==0:
        d.rectangle((x-10,134,x-1,157),fill=pants); d.rectangle((x+4,134,x+13,149),fill=pants); d.rectangle((x+9,147,x+22,157),fill=pants)
    else:
        d.rectangle((x-10,134,x-1,149),fill=pants); d.rectangle((x-20,147,x-7,157),fill=pants); d.rectangle((x+3,134,x+13,157),fill=pants)
    bx=x+45; by=58
    d.rounded_rectangle((bx,by,bx+132,by+38),9,outline=(110,110,105),width=2,fill=(20,20,20))
    d.polygon([(bx+10,by+38),(bx+22,by+38),(bx+15,by+48)],fill=(20,20,20))
    d.text((bx+16,by+9),"hello :)",font=F(BOLD,15),fill=(242,242,236))
    frames.append(im)
frames[0].save("assets/pixel-hello.gif",save_all=True,append_images=frames[1:],duration=90,loop=0,optimize=True,disposal=2)
print("generated project-software.gif + pixel-hello.gif")
