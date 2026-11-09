"""Render the public contribution calendar AS the road, never around a grid.

No token, private repository access, browser, or third-party stats service needed.
python scripts/render_circuit.py --refresh
"""
from __future__ import annotations

import argparse
import base64
import bisect
import html
import json
import io
import math
import re
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://github.com/users/lucazolvr/contributions"
W, H, FPS, FRAMES = 1000, 610, 20, 480
COLORS = ("#28213f", "#503777", "#8857bd", "#cba2ef", "#f1ce83")
BG, TEXT, MUTED, GOLD = "#0d0e20", "#f2edf9", "#bdb2d2", "#efd08f"


def font(size, bold=False):
    # Open fonts supplied by Ubuntu/Pillow, or the local OS; never redistribute OS fonts.
    names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
             "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def validate(data):
    days = data["days"]
    if not 350 <= len(days) <= 371:
        raise ValueError("Incomplete calendar: keeping the previous artwork")
    for index, day in enumerate(days):
        current = date.fromisoformat(day["date"])
        if type(day["count"]) is not int or day["count"] < 0 or day["level"] not in range(5):
            raise ValueError("Invalid contribution count or intensity")
        if index and (current - date.fromisoformat(days[index-1]["date"])).days != 1:
            raise ValueError("Calendar dates must be unique and consecutive")
    if data["total"] != sum(day["count"] for day in days):
        raise ValueError("Calendar total mismatch")
    return data


def parse_calendar(markup):
    tips = {}
    for attributes, body in re.findall(r'<tool-tip\b([^>]*)>(.*?)</tool-tip>', markup, re.S):
        target = re.search(r'\bfor="([^"]+)"', attributes)
        label = html.unescape(re.sub(r'<[^>]+>', '', body)).strip()
        count = re.match(r'([\d,]+) contributions?\b', label)
        if target and (count or label.startswith("No contributions")):
            tips[target[1]] = int(count[1].replace(',', '')) if count else 0
    days = []
    for attributes in re.findall(r'<td\b([^>]*)>', markup):
        stamp = re.search(r'\bdata-date="(\d{4}-\d{2}-\d{2})"', attributes)
        if not stamp:
            continue
        cell = re.search(r'\bid="([^"]+)"', attributes)
        level = re.search(r'\bdata-level="([0-4])"', attributes)
        if not cell or not level or cell[1] not in tips:
            raise ValueError("GitHub calendar markup changed; refusing fake or partial data")
        days.append(dict(date=stamp[1], count=tips[cell[1]], level=int(level[1])))
    days.sort(key=lambda d: d["date"])
    return validate(dict(login="lucazolvr", source=SOURCE,
                         updatedAt=datetime.now(timezone.utc).isoformat(), days=days,
                         total=sum(day["count"] for day in days)))


def cubic(a, b, c, d, t):
    return tuple((1-t)**3*a[k]+3*(1-t)**2*t*b[k]+3*(1-t)*t*t*c[k]+t**3*d[k] for k in (0, 1))


def make_track():
    # Closed racing line with an infield chicane; sampled by distance for a seamless lap.
    segments = [
        ((145, 386), (270, 386), (480, 386), (610, 386)),
        ((610, 386), (740, 386), (792, 358), (792, 296)),
        ((792, 296), (792, 241), (735, 230), (670, 230)),
        ((670, 230), (620, 230), (566, 230), (520, 230)),
        ((520, 230), (449, 230), (420, 206), (420, 167)),
        ((420, 167), (420, 126), (475, 114), (550, 114)),
        ((550, 114), (600, 114), (659, 114), (710, 114)),
        ((710, 114), (823, 114), (916, 132), (916, 270)),
        ((916, 270), (916, 427), (842, 476), (690, 476)),
        ((690, 476), (510, 476), (280, 476), (145, 476)),
        ((145, 476), (24, 476), (24, 386), (145, 386)),
    ]
    points = [cubic(*segment, step/100) for segment in segments for step in range(100)]
    points.append(points[0])
    distances = [0.0]
    for a, b in zip(points, points[1:]):
        distances.append(distances[-1]+math.dist(a, b))
    return points, distances


POINTS, DISTANCES = make_track()
LENGTH = DISTANCES[-1]


def pose(distance, offset=0):
    distance %= LENGTH
    index = min(len(POINTS)-2, max(0, bisect.bisect_right(DISTANCES, distance)-1))
    a, b = POINTS[index:index+2]
    fraction = (distance-DISTANCES[index])/(DISTANCES[index+1]-DISTANCES[index])
    angle = math.atan2(b[1]-a[1], b[0]-a[0])
    return (a[0]+(b[0]-a[0])*fraction-math.sin(angle)*offset,
            a[1]+(b[1]-a[1])*fraction+math.cos(angle)*offset, angle)


def road_tile(distance, length, low, high):
    return [pose(distance+length*step/4, low)[:2] for step in range(5)] + [
        pose(distance+length*step/4, high)[:2] for step in range(4, -1, -1)]


def draw_board(data, *, transparent=False):
    board = Image.new("RGBA", (W, H)) if transparent else Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(board)
    # Sparse print texture concentrated around the actual road, not a rectangular backdrop.
    if not transparent:
        for y in range(100, 525, 8):
            for x in range(30, 970, 8):
                intensity = math.exp(-((x-710)/340)**2-((y-330)/180)**2)
                if intensity > .16:
                    color = tuple(round(a+(b-a)*intensity*.34) for a, b in zip((13,14,32),(103,66,147)))
                    draw.rectangle((x,y,x+1,y+1), fill=color)
    draw.text((38, 27), "Circuito de Commits", font=font(30, True), fill=TEXT)
    draw.text((38, 69), "Contribuições que constroem o caminho.", font=font(16), fill=MUTED)
    draw.text((38, 139), f'{data["total"]:,}'.replace(',', '.'), font=font(47, True), fill=GOLD)
    draw.text((39, 197), "contribuições no período", font=font(16), fill=TEXT)
    active_days = sum(day['count'] > 0 for day in data['days'])
    current_streak = longest_streak = 0
    for day in data['days']:
        current_streak = current_streak+1 if day['count'] else 0
        longest_streak = max(longest_streak,current_streak)
    draw.text((39, 232), str(active_days), font=font(24, True), fill="#cba2ef")
    draw.text((186, 232), f'{longest_streak} dias', font=font(24, True), fill="#cba2ef")
    draw.text((39, 264), "dias ativos", font=font(12), fill=MUTED)
    draw.text((186, 264), "maior sequência", font=font(12), fill=MUTED)
    draw.text((39, 292), f'{len(data["days"])} dias · um bloco por dia', font=font(12), fill=MUTED)
    draw.line(POINTS, fill="#0a0918", width=76, joint="curve")
    # Discrete curbs, continuously following the racing line.
    for index in range(math.ceil(LENGTH/13)):
        d = index*13
        for side in (-1, 1):
            draw.polygon(road_tile(d, 11, side*34-2, side*34+2), fill=GOLD if index % 5 == 0 else "#7c58aa")
    columns = math.ceil(len(data["days"])/3)
    step = LENGTH/columns
    mapping = []
    for index, day in enumerate(data["days"]):
        column, lane = divmod(index, 3)
        d, low = column*step+1, -27+lane*18
        draw.polygon(road_tile(d, step-2, low, low+16), fill=COLORS[day["level"]])
        mapping.append(dict(**day, column=column, lane=lane, distance=round(d, 3)))
    # A small start/finish stripe crossing all three contribution lanes.
    for row in range(10):
        for col in range(2):
            draw.polygon(road_tile(47+col*4, 4, -29+row*6, -23+row*6),
                         fill="#f5eaff" if (row+col)%2 else "#171126")
    draw.text((163, 311), "LARGADA / CHEGADA", font=font(11, True), fill=GOLD)
    draw.text((38, 533), "MENOS", font=font(11, True), fill=MUTED)
    for index, color in enumerate(COLORS):
        draw.rounded_rectangle((93+index*24,532,110+index*24,549),radius=3,fill=color)
    draw.text((222, 533), "MAIS", font=font(11, True), fill=MUTED)
    days = data["days"]
    def fmt(value):
        return date.fromisoformat(value).strftime('%d/%m/%Y')
    period = f'{fmt(days[0]["date"])} — {fmt(days[-1]["date"])}'
    draw.text((W-38-draw.textlength(period,font=font(13)),534),period,font=font(13),fill=MUTED)
    updated = fmt(data["updatedAt"][:10])
    draw.text((38, 574), f'github.com/lucazolvr · Atualizado em {updated}', font=font(12), fill=MUTED)
    return board, mapping


def load_sprites():
    # Same authored 16-direction cat/kart turntable as the portfolio.
    sprites = []
    for index in range(16):
        with Image.open(ROOT/f'assets/kart/direction-{index:02}.webp') as source:
            sprites.append(source.convert("RGBA").resize((86,86), Image.Resampling.NEAREST))
    return sprites


def draw_frame(board, sprites, progress):
    frame = board.copy().convert("RGBA")
    draw = ImageDraw.Draw(frame)
    distance = progress*LENGTH+47
    x, y, angle = pose(distance)
    direction = round(math.degrees(angle)/22.5) % 16
    # Follow the track tangent with a small pixel exhaust, never a screen-wide effect.
    for age in range(5, 0, -1):
        tx, ty, _ = pose(distance-age*6)
        size = 1 if age > 3 else 2
        draw.rectangle((tx-size,ty-size,tx+size,ty+size), fill=GOLD if age%2 else "#a479d4")
    sprite = sprites[direction]
    # Baseline is registered at y=174 of the 192px source cells.
    frame.alpha_composite(sprite, (round(x-43),round(y-174/192*86+math.sin(progress*math.tau*36)*.6)))
    return frame.convert("RGB")


def circuit_markup(board, sprites, frames):
    """SVG layers shared by the standalone circuit and the profile panel."""
    def uri(image):
        buffer = io.BytesIO()
        image.save(buffer,format='PNG',optimize=True)
        return 'data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode('ascii')
    duration=frames/FPS
    positions, directions = [], []
    for index in range(frames+1):
        progress=index/frames
        x,y,angle=pose(progress*LENGTH+47)
        positions.append(f'{x-43:.2f} {y-174/192*86+math.sin(progress*math.tau*36)*.6:.2f}')
        directions.append(round(math.degrees(angle)/22.5)%16)
    pieces=['<style>.kart-still{display:none} @media(prefers-reduced-motion:reduce){.kart-moving{display:none}.kart-still{display:inline}}</style>',
            f'<image width="{W}" height="{H}" xlink:href="{uri(board)}"/>',
            '<defs>']
    for direction, sprite in enumerate(sprites):
        pieces.append(f'<image id="kart-{direction}" width="86" height="86" style="image-rendering:pixelated" xlink:href="{uri(sprite)}"/>')
    pieces.extend([
        '</defs>',
        '<g class="kart-moving">',
        f'<g transform="translate({positions[0]})"><animateTransform attributeName="transform" type="translate" values="{";".join(positions)}" dur="{duration}s" calcMode="linear" repeatCount="indefinite"/>',
    ])
    for direction in range(len(sprites)):
        # Retain only direction changes to keep the SVG small.
        keys=[0]+[i for i in range(1,frames+1) if directions[i]!=directions[i-1]]
        if keys[-1]!=frames:
            keys.append(frames)
        values=';'.join('1' if directions[i]==direction else '0' for i in keys)
        times=';'.join(f'{i/frames:.6f}' for i in keys)
        opacity=1 if direction==directions[0] else 0
        pieces.append(f'<use xlink:href="#kart-{direction}" opacity="{opacity}"><animate attributeName="opacity" values="{values}" keyTimes="{times}" calcMode="discrete" dur="{duration}s" repeatCount="indefinite"/></use>')
    pieces.extend(['</g></g>', f'<use class="kart-still" xlink:href="#kart-{directions[0]}" transform="translate({positions[0]})"/>'])
    return '\n'.join(pieces)


def write_svg(name, document):
    target = ROOT / 'assets' / name
    temporary = target.with_suffix('.tmp.svg')
    temporary.write_text(document + '\n', encoding='utf-8')
    temporary.replace(target)


def render_svg(board, sprites, frames):
    write_svg('commit-circuit.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
<title id="title">Circuito de Commits — Lucas de Oliveira</title>
<desc id="desc">Cada bloco da pista representa um dia real do calendário de contribuições.</desc>
{circuit_markup(board, sprites, frames)}
</svg>''')


def render(data, frames=FRAMES):
    from render_profile import profile_svgs

    board, mapping = draw_board(validate(data))
    sprites = load_sprites()
    still = draw_frame(board,sprites,0)
    still.save(ROOT/'assets/commit-circuit.png', optimize=True)
    render_svg(board,sprites,frames)
    panel_board, _ = draw_board(data, transparent=True)
    for name, document in profile_svgs(circuit_markup(panel_board, sprites, frames)):
        write_svg(name, document)
    # One shared palette prevents background flicker and allows tiny GIF delta frames.
    swatches = board.copy()
    for index, sprite in enumerate(sprites):
        swatches.paste(sprite,(index%8*110,index//8*100),sprite)
    palette = swatches.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    sequence = [draw_frame(board,sprites,index/frames).quantize(palette=palette,dither=Image.Dither.NONE)
                for index in range(frames)]
    temporary = ROOT/'assets/commit-circuit.tmp.gif'
    sequence[0].save(temporary,save_all=True,append_images=sequence[1:],duration=round(1000/FPS),
                     loop=0,disposal=1,optimize=True)
    temporary.replace(ROOT/'assets/commit-circuit.gif')
    (ROOT/'assets/circuit-map.json').write_text(json.dumps(dict(
        source=SOURCE,total=data['total'],dayCount=len(mapping),days=mapping),indent=2)+'\n',encoding='utf-8')
    print(f'Rendered {len(mapping)} real days as the road, {data["total"]} contributions, {frames} frames.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh',action='store_true')
    parser.add_argument('--frames',type=int,default=FRAMES)
    args = parser.parse_args()
    data_path = ROOT/'data/contributions.json'
    if args.refresh:
        request = Request(SOURCE,headers={'User-Agent':'lucazolvr-profile-circuit','Accept':'text/html'})
        with urlopen(request,timeout=30) as response:
            data = parse_calendar(response.read().decode('utf-8'))
    else:
        data = validate(json.loads(data_path.read_text(encoding='utf-8')))
    if args.frames < 2:
        raise ValueError('At least two animation frames are required')
    render(data,args.frames)
    data_path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
