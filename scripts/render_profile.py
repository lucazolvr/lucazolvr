"""Compose the continuous GitHub profile panel using local SVG artwork."""
import re
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

from render_header import pixel_field

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)

STACK_ROWS = (
    ('Linguagens', (
        ('TypeScript', 'typescript'), ('JavaScript', 'javascript'), ('Python', 'python'),
        ('Java', 'java'), ('HTML', 'html5'), ('CSS', 'css3'),
    )),
    ('Frontend, UI e mobile', (
        ('React / Native', 'react'), ('Next.js', 'nextjs'), ('Tailwind CSS', 'tailwindcss'),
        ('Vite', 'vitejs'), ('Three.js', 'threejs'), ('Flutter', 'flutter'),
    )),
    ('Backend e APIs', (
        ('Node.js', 'nodejs'), ('Fastify', 'fastify'), ('Spring Boot', 'spring'),
        ('Django', 'django'), ('NestJS', 'nestjs'), ('Postman', 'postman'), ('GitHub', 'github'),
    )),
    ('Dados e cache', (
        ('PostgreSQL', 'postgresql'), ('MySQL', 'mysql'), ('Redis', 'redis'), ('Prisma', 'prisma'),
    )),
)
NEW_LOGOS = {'html5', 'css3', 'vitejs', 'threejs', 'spring', 'django', 'postman', 'mysql', 'redis', 'prisma'}
CONTACT_TOP = 248
CONTACT_HEIGHT = 112
CONTENT_TOP = CONTACT_TOP + CONTACT_HEIGHT
PANEL_HEIGHT = 1636 + CONTACT_HEIGHT
CIRCUIT_Y = 923 + CONTACT_HEIGHT
CONTACTS = ('portfolio', 'linkedin', 'email', 'instagram')


def scope_icon_ids(icon, filename):
    # Separate logos often use identical gradient IDs such as "a" and "b".
    for element in icon.iter():
        for key, value in element.attrib.items():
            if key == 'id':
                element.set(key, f'{filename}-{value}')
            elif key.rsplit('}', 1)[-1] == 'href' and value.startswith('#'):
                element.set(key, f'#{filename}-{value[1:]}')
            elif 'url(#' in value:
                element.set(key, re.sub(r'url\(#([^)]+)\)', rf'url(#{filename}-\1)', value))


def stack_row(label, entries, top):
    pieces = [f'<text class="group-label" x="500" y="{top - 17}">{escape(label)}</text>']
    for index, (name, filename) in enumerate(entries):
        center = 500 + (index - (len(entries) - 1) / 2) * 121
        icon = ET.parse(ASSETS / 'stack' / f'{filename}.svg').getroot()
        scope_icon_ids(icon, filename)
        if filename in NEW_LOGOS:
            icon.attrib.update(x='12', y='12', width='40', height='40')
            if filename in {'threejs', 'prisma'}:
                icon.set('style', 'filter:brightness(0) invert(.9)')
            if filename == 'django':
                icon.set('fill', '#aee5c7')
            artwork = ET.tostring(icon, encoding='unicode')
            pieces.append(f'<g transform="translate({center - 32} {top})"><rect width="64" height="64" rx="12" fill="#191c2b"/>{artwork}</g>')
        else:
            icon.attrib.update(x=str(center - 32), y=str(top))
            if filename == 'fastify':
                icon.find(f'{{{SVG}}}rect').set('fill', '#bda9df')
            pieces.append(ET.tostring(icon, encoding='unicode'))
        pieces.append(f'<text class="tech-name" x="{center}" y="{top + 88}">{escape(name)}</text>')
    return '\n'.join(pieces)


def panel_slice(x, y, width, height, content, *, wave=False):
    # Every image samples the same surface coordinates, including the contact links.
    wave_artwork = f'<g id="panel-wave" shape-rendering="crispEdges">{pixel_field()}</g>' if wave else ''
    return f'''<svg xmlns="{SVG}" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="{x} {y} {width} {height}">
<defs>
  <clipPath id="panel-clip"><rect width="1000" height="{PANEL_HEIGHT}" rx="28"/></clipPath>
  <linearGradient id="panel-surface" x2=".26" y2="1">
    <stop stop-color="#101023"/><stop offset=".51" stop-color="#111024"/><stop offset="1" stop-color="#16112a"/>
  </linearGradient>
  <radialGradient id="panel-violet">
    <stop stop-color="#7449c6" stop-opacity=".38"/><stop offset="1" stop-color="#7449c6" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="panel-gold">
    <stop stop-color="#ddb17b" stop-opacity=".23"/><stop offset="1" stop-color="#ddb17b" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="panel-rule">
    <stop stop-color="#c0a2e6" stop-opacity=".07"/><stop offset=".5" stop-color="#c0a2e6" stop-opacity=".42"/>
    <stop offset="1" stop-color="#c0a2e6" stop-opacity=".07"/>
  </linearGradient>
  <pattern id="panel-dots" width="12" height="12" patternUnits="userSpaceOnUse">
    <rect width="1.5" height="1.5" fill="#baa0ed" opacity=".14"/>
  </pattern>
{wave_artwork}
</defs>
<g clip-path="url(#panel-clip)">
  <rect width="1000" height="{PANEL_HEIGHT}" fill="url(#panel-surface)"/>
  <ellipse cx="123" cy="170" rx="415" ry="315" fill="url(#panel-violet)"/>
  <ellipse cx="849" cy="525" rx="455" ry="434" fill="url(#panel-violet)"/>
  <ellipse cx="222" cy="{CIRCUIT_Y + 373}" rx="482" ry="365" fill="url(#panel-violet)"/>
  <ellipse cx="821" cy="{PANEL_HEIGHT - 166}" rx="398" ry="226" fill="url(#panel-gold)"/>
  <rect width="1000" height="{PANEL_HEIGHT}" fill="url(#panel-dots)"/>
  {content}
</g>
<rect x=".5" y=".5" width="999" height="{PANEL_HEIGHT - 1}" rx="27.5" fill="none" stroke="#46365e"/>
</svg>'''


PANEL_STYLES = '''<style>
  .panel-text { font-family: Arial, Helvetica, sans-serif; text-anchor: middle; }
  .group-label { font-size: 19px; font-weight: 700; fill: #ddc6fa; }
  .tech-name { font-size: 16px; fill: #e5d9f5; }
  .pixel-motion { animation: panel-drift 11s ease-in-out infinite alternate; }
  .pixel-footer { animation-delay: -5s; }
  @keyframes panel-drift { from { transform: translateY(-4px) } to { transform: translateY(0) } }
  @media (prefers-reduced-motion: reduce) { .pixel-motion { animation: none } }
</style>'''


def profile_svgs(circuit):
    intro = f'''{PANEL_STYLES}
  <g class="pixel-motion" opacity=".67">
    <use xlink:href="#panel-wave" transform="translate(0 236) scale(1 -1)"/>
  </g>
  <g class="panel-text">
    <path d="M500 36l6 6-6 6-6-6z" fill="#efd08f"/>
    <text x="500" y="110" font-size="58" font-weight="700" fill="#f5effc">Lucas de Oliveira</text>
    <text x="500" y="152" font-size="25" fill="#efd08f">Desenvolvedor web e mobile</text>
    <text x="500" y="200" font-size="20" fill="#ddd3ed">Construo interfaces, aplicativos e integrações
      <tspan x="500" dy="28">com atenção à experiência de quem usa.</tspan>
    </text>
  </g>'''
    yield 'profile-intro.svg', panel_slice(0, 0, 1000, CONTACT_TOP, intro, wave=True)

    for index, name in enumerate(CONTACTS):
        badge = ET.parse(ASSETS / f'contact-{name}.svg').getroot()
        scale = 1.54
        x = index * 250
        left = x + (250 - int(badge.attrib['width']) * scale) / 2
        top = CONTACT_TOP + (CONTACT_HEIGHT - int(badge.attrib['height']) * scale) / 2
        artwork = ET.tostring(badge, encoding='unicode')
        contact = f'<g transform="translate({left} {top}) scale({scale})">{artwork}</g>'
        yield f'profile-contact-{name}.svg', panel_slice(x, CONTACT_TOP, 250, CONTACT_HEIGHT, contact)

    stack = '\n'.join(stack_row(label, entries, 367 + CONTACT_HEIGHT + index * 138)
                      for index, (label, entries) in enumerate(STACK_ROWS))
    body = f'''{PANEL_STYLES}
  <g opacity=".42" transform="translate(1000 {PANEL_HEIGHT - 240}) scale(-1 1)">
    <g class="pixel-motion pixel-footer"><use xlink:href="#panel-wave"/></g>
  </g>
  <g fill="url(#panel-rule)">
    <rect x="64" y="{280 + CONTACT_HEIGHT}" width="872" height="1"/>
    <rect x="64" y="{CIRCUIT_Y - 20}" width="872" height="1"/>
    <rect x="64" y="{PANEL_HEIGHT - 127}" width="872" height="1"/>
  </g>
  <g class="panel-text">
    <text x="500" y="{320 + CONTACT_HEIGHT}" font-size="28" font-weight="700" fill="#f5effc">Tecnologias</text>
    {stack}
  </g>
  <g transform="translate(25 {CIRCUIT_Y}) scale(.95)">
    {circuit}
  </g>
  <text class="panel-text" x="500" y="{PANEL_HEIGHT - 70}" font-size="21" font-style="italic" fill="#eee1f9">O importante é o que se faz, não o que se diz.</text>'''
    yield 'profile-content.svg', panel_slice(0, CONTENT_TOP, 1000, PANEL_HEIGHT - CONTENT_TOP, body, wave=True)
