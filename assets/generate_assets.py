from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFilter

ASSET_DIR = Path(__file__).resolve().parent
PNG = ASSET_DIR / "cheburek.png"
ICO = ASSET_DIR / "cheburek.ico"
S = 3
N = 512 * S

# Paint a crisp, original icon at 3x resolution, then downsample for smooth edges.
image = Image.new("RGB", (N, N), "#0b0811")
px = image.load()
for y in range(N):
    for x in range(N):
        nx, ny = x / N, y / N
        blend = (nx * 0.35 + ny * 0.65)
        px[x, y] = (
            int(9 + 19 * blend),
            int(7 + 4 * (1 - blend)),
            int(17 + 10 * blend),
        )

glow = Image.new("RGBA", (N, N), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse((55*S, 70*S, 455*S, 470*S), fill=(255, 28, 103, 95))
glow = glow.filter(ImageFilter.GaussianBlur(34*S))
image = Image.alpha_composite(image.convert("RGBA"), glow)
draw = ImageDraw.Draw(image)

# Rounded icon border and neon rim
draw.rounded_rectangle((12*S, 12*S, 500*S, 500*S), radius=100*S,
                       outline=(255, 43, 116, 255), width=5*S)
draw.rounded_rectangle((22*S, 22*S, 490*S, 490*S), radius=90*S,
                       outline=(117, 24, 71, 255), width=2*S)

# Orbit lines and star pixels
draw.arc((25*S, 65*S, 485*S, 460*S), 202, 337, fill=(255, 53, 124, 255), width=8*S)
draw.arc((60*S, 35*S, 455*S, 475*S), 20, 150, fill=(216, 28, 100, 220), width=4*S)
for x, y, r in [(76,146,8),(420,105,7),(426,342,8),(96,380,5),(390,169,4),(130,92,4)]:
    draw.polygon([(x*S,(y-r)*S),((x+r//2)*S,y*S),(x*S,(y+r)*S),((x-r//2)*S,y*S)],
                 fill=(255, 111, 168, 255))
for x, y in [(88,300),(413,390),(373,80),(130,435)]:
    draw.rounded_rectangle((x*S,y*S,(x+8)*S,(y+8)*S), radius=2*S, fill=(255,43,116,230))

# Crown behind the shield
crown = [(178,120),(194,70),(231,105),(256,51),(282,105),(319,70),(335,120),(322,151),(190,151)]
draw.polygon([(x*S,y*S) for x,y in crown], fill=(130,55,19,255), outline=(255,217,103,255))
crown2 = [(185,116),(198,84),(232,113),(256,66),(280,113),(314,84),(328,116),(317,142),(195,142)]
draw.polygon([(x*S,y*S) for x,y in crown2], fill=(255,190,50,255), outline=(255,237,151,255))
draw.polygon([(256*S,82*S),(270*S,106*S),(256*S,128*S),(242*S,106*S)],
             fill=(255,47,115,255), outline=(255,245,183,255), width=4*S)

# Cheburek/shield silhouette
outer = [(256,135),(304,160),(367,173),(414,200),(432,242),(423,292),(389,347),(337,389),(256,440),
         (175,389),(123,347),(89,292),(80,242),(98,200),(145,173),(208,160)]
draw.polygon([(x*S,y*S) for x,y in outer], fill=(79,23,36,255), outline=(255,55,119,255))
mid = [(256,151),(302,174),(360,187),(398,211),(413,246),(402,287),(373,333),(325,371),(256,415),
       (187,371),(139,333),(110,287),(99,246),(114,211),(152,187),(210,174)]
draw.polygon([(x*S,y*S) for x,y in mid], fill=(255,164,44,255), outline=(255,231,152,255), width=6*S)
inner = [(256,190),(296,206),(350,218),(381,237),(390,258),(373,293),(346,324),(307,352),(256,382),
         (205,352),(166,324),(139,293),(122,258),(131,237),(162,218),(216,206)]
draw.polygon([(x*S,y*S) for x,y in inner], fill=(19,10,25,255), outline=(255,213,103,255), width=6*S)

# Golden crust highlights
for x,y,r in [(156,231,9),(185,211,5),(220,218,8),(300,216,7),(341,232,9),(147,286,6),(365,286,7),(197,338,7),(318,340,7)]:
    draw.ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S), fill=(255,205,79,255))
draw.arc((112*S,205*S,402*S,378*S), 197, 335, fill=(255,238,164,255), width=4*S)

# Neon globe and connected network
draw.ellipse((157*S,218*S,355*S,416*S), fill=(176,16,74,255), outline=(255,89,147,255), width=6*S)
draw.ellipse((172*S,233*S,340*S,401*S), fill=(30,10,34,255), outline=(255,61,128,255), width=3*S)
draw.arc((186*S,233*S,326*S,401*S), 65, 295, fill=(255,97,158,230), width=3*S)
draw.arc((186*S,233*S,326*S,401*S), 245, 115, fill=(255,97,158,230), width=3*S)
draw.arc((172*S,270*S,340*S,360*S), 0, 180, fill=(255,73,145,230), width=3*S)
draw.arc((172*S,290*S,340*S,383*S), 180, 360, fill=(255,73,145,230), width=3*S)
nodes = [(197,311),(235,274),(282,309),(319,266),(223,358),(312,357)]
edges = [(0,1),(1,2),(2,3),(0,4),(4,2),(2,5),(5,3)]
for a,b in edges:
    draw.line((nodes[a][0]*S,nodes[a][1]*S,nodes[b][0]*S,nodes[b][1]*S), fill=(255,105,167,255), width=4*S)
for x,y in nodes:
    r = 9 if (x,y) in (nodes[1],nodes[3]) else 7
    draw.ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S), fill=(255,235,194,255), outline=(255,69,139,255), width=3*S)

image = image.convert("RGB").resize((512, 512), Image.Resampling.LANCZOS)
# Mask rounded corners so the icon looks clean in launchers and shortcuts.
mask = Image.new("L", (512, 512), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, 511, 511), radius=100, fill=255)
image = image.convert("RGBA")
image.putalpha(mask)
image.save(PNG, optimize=True)
image.save(ICO, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print(f"Generated {PNG.name} and {ICO.name}")
