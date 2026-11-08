"""Self-contained ordered-dither header, adapted from the portfolio's PixelField.

No browser runtime, JavaScript, external assets or image service in the README.
Run: python scripts/render_header.py
"""
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT, STEP = 1000, 240, 4
BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]
BACKGROUND = (13, 17, 23)
PALETTE = [BACKGROUND, (30, 25, 51), (57, 35, 93), (91, 49, 148),
           (147, 91, 210), (200, 158, 243), (164, 115, 222), (104, 62, 164), (59, 36, 104)]


def clamp(value, lower=0, upper=1):
    return max(lower, min(upper, value))


def pixel_field():
    groups = defaultdict(list)
    for column, x in enumerate(range(0, WIDTH, STEP)):
        u = x/WIDTH
        # Higher at both edges, irregular contours, clean fixed island behind the copy.
        sides = (abs(u-.5)*2)**3
        irregular = math.sin(u*10.7)*7+math.sin(u*21.3+.9)*4+math.sin(u*35.1+1.8)*2
        boundary = 208-sides*112+irregular
        light = math.exp(-((u-.16)/.23)**2)
        for row, y in enumerate(range(0, HEIGHT, STEP)):
            if 265 < x < 735 and y < 178:
                continue
            depth = y-boundary
            threshold = (BAYER[(row%4)*4+column%4]+.5)/16
            level = clamp((depth+17)/10.5,0,8)
            low = math.floor(level)
            color = PALETTE[min(8,low+(level-low > threshold))]
            if color == BACKGROUND:
                continue
            gold = math.exp(-((depth-34)/25)**2)*light*.76
            warmth = clamp(math.floor(gold*5+threshold)/5)
            color = tuple(round(a+(b-a)*warmth) for a,b in zip(color,(235,187,113)))
            fill = '#'+''.join(f'{value:02x}' for value in color)
            groups[fill].append(f'M{x} {y}h{STEP}v{STEP}h-{STEP}z')
    return ''.join(f'<path fill="{color}" d="{"".join(cells)}"/>' for color,cells in groups.items())


def render():
    field = pixel_field()
    document = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">Lucas de Oliveira — Desenvolvedor web e mobile</title>
<desc id="desc">Ondas de pixels roxos, lilás e dourados sobem pelas laterais e deixam o centro livre para o nome.</desc>
<defs><clipPath id="frame"><rect width="{WIDTH}" height="{HEIGHT}" rx="12"/></clipPath></defs>
<style>.pixels{{animation:drift 11s ease-in-out infinite alternate}}@keyframes drift{{from{{transform:translateY(0)}}to{{transform:translateY(4px)}}}}@media(prefers-reduced-motion:reduce){{.pixels{{animation:none}}}}</style>
<g clip-path="url(#frame)"><rect width="{WIDTH}" height="{HEIGHT}" fill="#0d1117"/>
<g class="pixels" shape-rendering="crispEdges">{field}</g>
<g font-family="Arial,Helvetica,sans-serif" text-anchor="middle"><text x="500" y="88" font-size="48" font-weight="700" fill="#f1edf9" letter-spacing="-1.3">Lucas de Oliveira</text><text x="500" y="127" font-size="21" fill="#c6afff">Desenvolvedor web &amp; mobile</text><text x="500" y="157" font-size="14" fill="#bbb4ca">Interfaces · Aplicativos · Integrações</text></g></g></svg>
'''
    target = ROOT/'assets/header-pixel.svg'
    target.write_text(document,encoding='utf-8')
    print(f'Ordered-dither header: {target.stat().st_size:,} bytes, no runtime dependencies.')


if __name__ == '__main__':
    render()
