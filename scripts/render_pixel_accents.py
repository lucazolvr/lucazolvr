"""Render the profile's lightweight, self-contained animated pixel accents."""
import math
from collections import defaultdict
from pathlib import Path

from render_header import BAYER, PALETTE, BACKGROUND, clamp

ROOT = Path(__file__).resolve().parents[1]


def render(name, height, divider=False):
    groups = defaultdict(list)
    step = 4
    for col, x in enumerate(range(0, 1000, step)):
        u = x / 1000
        wave = math.sin(u * 11.4 + .5) * 5 + math.sin(u * 24.6) * 3
        boundary = (height * .43 + wave) if not divider else 6 + wave * .33
        for row, y in enumerate(range(0, height + 8, step)):
            threshold = (BAYER[(row % 4) * 4 + col % 4] + .5) / 16
            depth = y - boundary
            level = clamp((depth + 14) / (7 if not divider else 2.6), 0, 8)
            low = math.floor(level)
            color = PALETTE[min(8, low + (level - low > threshold))]
            if color == BACKGROUND:
                continue
            # Both accents dissolve at their edges rather than ending in a bar.
            fade = clamp(min(u, 1-u) * (9 if divider else 16))
            if divider:
                fade *= clamp((height - y) / 8)
            gold = math.exp(-((u - (.75 if not divider else .25)) / .21) ** 2)
            gold *= math.exp(-((depth - (22 if not divider else 6)) / 17) ** 2) * .82
            color = tuple(round((a + (b-a)*gold)*fade + base*(1-fade))
                          for a, b, base in zip(color, (239, 208, 143), BACKGROUND))
            fill = '#' + ''.join(f'{c:02x}' for c in color)
            groups[fill].append(f'M{x} {y}h4v4h-4z')
    paths = ''.join(f'<path fill="{color}" d="{"".join(cells)}"/>'
                    for color, cells in groups.items())
    document = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}">
<defs><clipPath id="bounds"><rect width="1000" height="{height}" rx="8"/></clipPath></defs>
<style>.tide{{animation:tide 9s ease-in-out infinite alternate}}@keyframes tide{{from{{transform:translateY(0)}}to{{transform:translateY(4px)}}}}@media(prefers-reduced-motion:reduce){{.tide{{animation:none}}}}</style>
<g clip-path="url(#bounds)"><rect width="1000" height="{height}" fill="#0d1117"/><g class="tide" shape-rendering="crispEdges">{paths}</g></g></svg>
'''
    target = ROOT / 'assets' / name
    target.write_text(document, encoding='utf-8')
    print(f'{name}: {target.stat().st_size:,} bytes')


if __name__ == '__main__':
    render('footer-pixel.svg', 96)
    render('divider-pixel.svg', 28, divider=True)
