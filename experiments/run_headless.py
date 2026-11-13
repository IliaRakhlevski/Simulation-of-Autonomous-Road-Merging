"""Run roads_merge_simulation.py headless and record the outcome of every episode.

Usage: python experiments/run_headless.py roads_merge_simulation.py <out.csv> <episodes> <seed> <learning: 1|0>

pygame is replaced by a minimal stub: drawing is a no-op, while pygame.Rect is
re-implemented with the same integer semantics (move_ip, colliderect, edge properties),
which is all the simulation logic uses. The simulation source is executed unchanged,
except that its interactive main loop is replaced by the loop below (no 40 FPS limit).
With learning=0 the security-area update after a crash is disabled.
"""
import contextlib
import csv
import io
import os
import random
import sys
import types

sim_path, out_path, n_episodes, seed, learning = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5] == '1'


class Rect:
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x, self.y, self.w, self.h = int(x), int(y), int(w), int(h)

    left = property(lambda s: s.x, lambda s, v: setattr(s, 'x', int(v)))
    top = property(lambda s: s.y, lambda s, v: setattr(s, 'y', int(v)))
    right = property(lambda s: s.x + s.w, lambda s, v: setattr(s, 'x', int(v) - s.w))
    bottom = property(lambda s: s.y + s.h, lambda s, v: setattr(s, 'y', int(v) - s.h))

    def move_ip(self, dx, dy):
        self.x += int(dx)
        self.y += int(dy)

    def colliderect(self, o):
        # pygame semantics: positive-area overlap; touching edges do not collide
        return (self.w > 0 and self.h > 0 and o.w > 0 and o.h > 0 and
                self.x < o.x + o.w and o.x < self.x + self.w and
                self.y < o.y + o.h and o.y < self.y + self.h)


class Surface:
    def __init__(self, w=1, h=1):
        self.w, self.h = w, h

    def get_rect(self):
        return Rect(0, 0, self.w, self.h)

    def blit(self, *a, **k):
        pass

    def fill(self, *a, **k):
        pass


class Font:
    def render(self, *a, **k):
        return Surface()


pg = types.ModuleType('pygame')
pg.Rect = Rect
pg.QUIT = 256
pg.init = lambda: None
pg.quit = lambda: None
pg.image = types.SimpleNamespace(load=lambda path: Surface())
pg.transform = types.SimpleNamespace(scale=lambda s, size: Surface(*size), rotate=lambda s, a: s)
pg.display = types.SimpleNamespace(set_mode=lambda size: Surface(*size), set_caption=lambda t: None,
                                   update=lambda: None)
pg.draw = types.SimpleNamespace(line=lambda *a, **k: None)
pg.font = types.SimpleNamespace(SysFont=lambda *a, **k: Font())
pg.time = types.SimpleNamespace(Clock=lambda: types.SimpleNamespace(tick=lambda fps: None))
pg.event = types.SimpleNamespace(get=lambda: [])
sys.modules['pygame'] = pg

random.seed(seed)
src = open(sim_path, encoding='utf8').read()
src = src.split('# =================== main loop')[0]
ns = {'__name__': 'sim'}
exec(compile(src, sim_path, 'exec'), ns)
env = ns['env']
if not learning:
    env.update_coll_shifts = lambda: None

rows = []
prev_ep, prev_crash, frames = env.num_episodes, env.num_crashes, 0
sink = io.StringIO()
while len(rows) < n_episodes:
    with contextlib.redirect_stdout(sink):
        env.Step()
        env.Update()
    frames += 1
    if env.num_episodes != prev_ep:
        crashed = env.num_crashes != prev_crash
        rows.append((len(rows) + 1, int(crashed), frames, env.left_coll_shift, env.right_coll_shift,
                     round(env.tc_speed_factor, 4)))
        prev_ep, prev_crash, frames = env.num_episodes, env.num_crashes, 0
    if len(sink.getvalue()) > 1_000_000:
        sink = io.StringIO()

os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
with open(out_path, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['episode', 'crash', 'frames', 'left_shift', 'right_shift', 'speed_factor'])
    w.writerows(rows)
print(f'seed={seed} learning={learning} episodes={len(rows)} crashes={sum(r[1] for r in rows)}')
