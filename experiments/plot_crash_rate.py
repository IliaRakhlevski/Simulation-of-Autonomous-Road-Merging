"""Build an SVG chart of the crash rate per block of episodes (no matplotlib).

Usage: python experiments/plot_crash_rate.py <dir with run_s<seed>_L<0|1>.csv files> <svg_path>
"""
import csv
import glob
import os
import sys

d, out = sys.argv[1], sys.argv[2]
BLOCK = 50
W, H = 1120, 480
L, R, T, B = 80, 300, 90, 60          # plot margins
PW, PH = W - L - R, H - T - B
XMAX, YMAX = 2000, 60
SURFACE, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df'
SERIES = [(0, '#eb6834', 'Without learning'), (1, '#2a78d6', 'With adaptive security area')]


def sx(v):
    return L + v / XMAX * PW


def sy(v):
    return T + PH - v / YMAX * PH


def load(flag):
    runs = []
    for f in sorted(glob.glob(os.path.join(d, f'run_s*_L{flag}.csv'))):
        with open(f) as fh:
            runs.append([int(r['crash']) for r in csv.DictReader(fh)])
    n = min(len(r) for r in runs) // BLOCK
    blocks = [[sum(r[i * BLOCK:(i + 1) * BLOCK]) / BLOCK * 100 for i in range(n)] for r in runs]
    xs = [(i + 1) * BLOCK for i in range(n)]
    mean = [sum(b[i] for b in blocks) / len(blocks) for i in range(n)]
    lo = [min(b[i] for b in blocks) for i in range(n)]
    hi = [max(b[i] for b in blocks) for i in range(n)]
    tail = sum(sum(r[1000:2000]) for r in runs) / sum(len(r[1000:2000]) for r in runs) * 100
    return xs, mean, lo, hi, tail


parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="\'Segoe UI\', Arial, Helvetica, sans-serif">',
         f'<defs><clipPath id="plot"><rect x="{L}" y="{T}" width="{PW}" height="{PH}"/></clipPath></defs>',
         f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>',
         f'<text x="{L}" y="38" font-size="20" font-weight="700" fill="{INK}">Crash rate during learning</text>',
         f'<text x="{L}" y="62" font-size="14" fill="{INK2}">Share of merges ending in a crash, per {BLOCK} episodes · '
         f'mean of 5 runs with different traffic, band = min–max</text>']

for v in range(0, YMAX + 1, 10):
    y = sy(v)
    parts.append(f'<line x1="{L}" y1="{y:.1f}" x2="{L + PW}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
    parts.append(f'<text x="{L - 10}" y="{y + 5:.1f}" font-size="13" fill="{INK2}" text-anchor="end">{v}%</text>')
for v in range(0, XMAX + 1, 250):
    parts.append(f'<text x="{sx(v):.1f}" y="{T + PH + 22}" font-size="13" fill="{INK2}" text-anchor="middle">{v}</text>')
parts.append(f'<text x="{L + PW / 2:.1f}" y="{H - 12}" font-size="13" fill="{INK2}" text-anchor="middle">Episode</text>')

for flag, color, name in SERIES:
    xs, mean, lo, hi, tail = load(flag)
    band = ' '.join(f'{sx(x):.1f},{sy(v):.1f}' for x, v in zip(xs, hi)) + ' ' + \
           ' '.join(f'{sx(x):.1f},{sy(v):.1f}' for x, v in reversed(list(zip(xs, lo))))
    parts.append(f'<polygon points="{band}" fill="{color}" fill-opacity="0.13" stroke="none" clip-path="url(#plot)"/>')
    line = ' '.join(f'{sx(x):.1f},{sy(v):.1f}' for x, v in zip(xs, mean))
    parts.append(f'<polyline points="{line}" fill="none" stroke="{color}" stroke-width="2.5" '
                 f'stroke-linejoin="round" stroke-linecap="round"/>')
    ly = sy(mean[-1])
    parts.append(f'<circle cx="{sx(xs[-1]):.1f}" cy="{ly:.1f}" r="4" fill="{color}" stroke="{SURFACE}" stroke-width="2"/>')
    parts.append(f'<text x="{L + PW + 16}" y="{ly - 4:.1f}" font-size="14" font-weight="700" fill="{INK}">{name}</text>')
    parts.append(f'<text x="{L + PW + 16}" y="{ly + 15:.1f}" font-size="13" fill="{INK2}">'
                 f'{tail:.0f}% crashes in episodes 1001–2000</text>')
    print(name, 'first block', round(mean[0], 1), 'tail', round(tail, 1))

parts.append('</svg>')
open(out, 'w', encoding='utf8').write('\n'.join(parts))
print('saved', out)
