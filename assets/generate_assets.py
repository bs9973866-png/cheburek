from pathlib import Path

import cairosvg
from PIL import Image

ASSET_DIR = Path(__file__).resolve().parent
SVG = ASSET_DIR / "cheburek.svg"
PNG = ASSET_DIR / "cheburek.png"
ICO = ASSET_DIR / "cheburek.ico"

cairosvg.svg2png(url=str(SVG), write_to=str(PNG), output_width=512, output_height=512)
with Image.open(PNG) as image:
    icon = image.convert("RGBA")
    icon.save(ICO, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

print(f"Generated {PNG.name} and {ICO.name}")
