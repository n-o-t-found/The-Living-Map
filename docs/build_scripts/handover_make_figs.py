import sys
sys.path.insert(0, '/home/claude/writer_sim')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from sim_world import World
import viz

GREEN, GREY, BLUE, ORANGE, RED = '#d9ead3', '#eeeeee', '#dbe8f5', '#fde9c9', '#b00020'

def box(ax, x, y, w, h, text, fc, ec='#333', fs=8.5, bold=False, ls='-'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.12', fc=fc, ec=ec, lw=1.2, ls=ls))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs, weight='bold' if bold else 'normal')

def arrow(ax, p, q, text=None, color='#222', ls='-', off=(0, 0.12), fs=7, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=11, lw=1.3, color=color, ls=ls,
                                 connectionstyle=f'arc3,rad={rad}'))
    if text:
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, ha='center', va='bottom', fontsize=fs, color=color)

# ---------------------------------------------------------------- architecture
fig, ax = plt.subplots(figsize=(10, 5.8))
ax.set_xlim(0, 20); ax.set_ylim(-1.0, 11.6); ax.axis('off')
ax.text(10, 11.2, 'Writer explores -> beacons deposited -> Outside Network receives & translates -> command post -> Executor navigates by beacons',
        ha='center', fontsize=7.5, style='italic')
# column 1: building
ax.add_patch(Rectangle((0.3, 1.8), 5.7, 8.2, fc='#fafafa', ec='#555', lw=1.5))
ax.text(3.15, 9.55, 'THE BUILDING', ha='center', fontsize=9.5, weight='bold')
ax.text(3.15, 9.1, '(no GPS, no network)', ha='center', fontsize=8)
box(ax, 1.0, 6.4, 4.3, 1.9, 'WRITER robot\nexplores, detects events\n(hazard, junction, hole),\ndecides, drops beacons', GREEN, bold=True, fs=8)
box(ax, 1.0, 3.0, 4.3, 1.6, 'BEACONS on the ground\n(small RF broadcasters)', GREY, bold=True, fs=8)
arrow(ax, (3.15, 6.4), (3.15, 4.6))
ax.text(3.35, 5.5, 'I1: write message\n+ drop', fontsize=8, va='center')
# radio stops
ax.plot([6.6, 6.6], [1.5, 10.3], color=RED, ls='--', lw=1.7)
ax.text(6.6, 10.55, 'RADIO STOPS', color=RED, ha='center', fontsize=8.5, weight='bold')
# column 2: outside network
ax.add_patch(FancyBboxPatch((7.3, 1.8), 6.1, 8.2, boxstyle='round,pad=0.02,rounding_size=0.2', fc=BLUE, ec='#1f4e79', lw=1.6, ls='--'))
ax.text(10.35, 9.55, 'OUTSIDE NETWORK AREA', ha='center', fontsize=9.5, weight='bold', color='#1f4e79')
ax.text(10.35, 9.1, '(GPS, satellite time, links)', ha='center', fontsize=8, color='#1f4e79')
ys = [7.2, 5.3, 3.4, 1.9]
labels = ['1  RECEIVE\nlog from the Writer', '2  TRANSLATE\nprivate frame -> GPS', '3  CARRY\nto the command post', '4  BRIEF\nmission for the Executor']
ys = [7.35, 5.6, 3.85, 2.1]
for y, t in zip(ys, labels):
    box(ax, 8.0, y, 4.7, 1.2, t, GREY, fs=8.5)
for a, b in zip(ys[:-1], ys[1:]):
    arrow(ax, (10.35, a), (10.35, b + 1.2))
# I3
arrow(ax, (5.3, 7.95), (8.0, 7.95))
ax.text(5.95, 8.15, 'I3', ha='center', va='bottom', fontsize=8.5, weight='bold')
# column 3
box(ax, 15.0, 3.6, 4.6, 1.7, 'COMMAND POST\nlive map', GREY, bold=True, fs=9)
box(ax, 15.0, 1.9, 4.6, 1.3, 'EXECUTOR robot\nbriefed, then enters', GREY, bold=True, fs=8.5)
arrow(ax, (12.7, 4.45), (15.0, 4.45))
ax.text(14.2, 4.65, 'I4', ha='center', va='bottom', fontsize=8.5, weight='bold')
arrow(ax, (12.7, 2.55), (15.0, 2.55))
ax.text(14.2, 2.75, 'I5', ha='center', va='bottom', fontsize=8.5, weight='bold')
# I2: executor listens to beacons (elbow path below everything)
ax.plot([17.3, 17.3], [1.9, 0.7], color='#222', lw=1.3, ls='--')
ax.plot([17.3, 3.15], [0.7, 0.7], color='#222', lw=1.3, ls='--')
arrow(ax, (3.15, 0.7), (3.15, 3.0), ls='--')
ax.text(10.3, 0.85, 'I2: inside the building, the Executor listens to the beacons (RF broadcast)', ha='center', va='bottom', fontsize=7.5)
# legend
ax.add_patch(Rectangle((0.3, -0.85), 0.5, 0.4, fc=GREEN, ec='#333')); ax.text(0.95, -0.65, 'implemented in the Python simulation (Writer only)', fontsize=7.5, va='center')
ax.add_patch(Rectangle((10.3, -0.85), 0.5, 0.4, fc=GREY, ec='#333')); ax.text(10.95, -0.65, 'designed only - not implemented, not simulated', fontsize=7.5, va='center')
fig.tight_layout(); fig.savefig('/home/claude/handover/fig/architecture.png', dpi=170); plt.close(fig)

# ---------------------------------------------------------------- state machine
fig, ax = plt.subplots(figsize=(10, 5.4))
ax.set_xlim(0, 13.8); ax.set_ylim(0.4, 8.4); ax.axis('off')
S = {'CALIBRATE': (1.4, 4.6), 'EXPLORE': (5.0, 4.6), 'DROP': (9.0, 4.6), 'RECOVER': (5.0, 7.0),
     'RETURN': (5.0, 2.2), 'UPLOAD': (9.0, 2.2), 'DONE': (12.4, 2.2), 'SAFE_STOP': (12.4, 6.9)}
for n, (x, y) in S.items():
    box(ax, x - 1.0, y - 0.45, 2.0, 0.9, n, GREEN if n != 'SAFE_STOP' else '#f8d7da', bold=True, fs=9)
arrow(ax, (2.4, 4.6), (4.0, 4.6), 'gyro calibrated\n(3 s standing still)', off=(0, 0.12), fs=6.8)
arrow(ax, (6.0, 4.78), (8.0, 4.78), 'event accepted by policy', off=(0, 0.08), fs=7)
arrow(ax, (8.0, 4.42), (6.0, 4.42))
ax.text(7.0, 4.3, 'dropped / failed after retry', ha='center', va='top', fontsize=6.8)
arrow(ax, (4.7, 5.05), (4.7, 6.55))
ax.text(4.6, 5.8, 'stuck (1st)', ha='right', va='center', fontsize=7)
arrow(ax, (5.3, 6.55), (5.3, 5.05))
ax.text(5.4, 5.8, 'back up + turn,\nthen resume', ha='left', va='center', fontsize=7)
arrow(ax, (5.0, 4.15), (5.0, 2.65))
ax.text(4.9, 3.4, 'magazine empty, battery reserve,\ntime limit, or stuck (2nd)', ha='right', va='center', fontsize=7)
arrow(ax, (6.0, 2.2), (8.0, 2.2))
ax.text(7.0, 2.35, 'back at entrance', ha='center', va='bottom', fontsize=7)
arrow(ax, (5.9, 4.15), (8.2, 2.65), color='#444')
ax.text(8.2, 3.4, 'exploration complete\n(back at start)', ha='left', va='center', fontsize=7, color='#444')
arrow(ax, (10.0, 2.2), (11.4, 2.2))
ax.text(10.7, 2.35, 'sent, or\n3 tries', ha='center', va='bottom', fontsize=6.8)
box(ax, 7.4, 6.45, 2.2, 0.9, 'ANY STATE', '#ffffff', fs=8.5, ls='--')
arrow(ax, (9.6, 6.9), (11.4, 6.9), color=RED)
ax.text(10.5, 7.05, 'tilt > 35 deg', ha='center', va='bottom', fontsize=7.5, color=RED)
ax.text(0.2, 0.95, 'EXPLORE contains: wall following, event detection, beacon decision, breadcrumb trail.   '
        'UPLOAD sends the log only if the robot is near the entrance.\nRETURN retraces the loop-erased breadcrumb trail.', fontsize=7.5, style='italic')
fig.tight_layout(); fig.savefig('/home/claude/handover/fig/state_machine.png', dpi=170); plt.close(fig)

# ---------------------------------------------------------------- simulated building (static)
w = World(with_debris=False)
fig, ax = plt.subplots(figsize=(8, 4.7))
viz._draw_map(ax, w)
for t, (x, y) in {'MAIN CORRIDOR (1 m wide)': (11.0, 4.0), 'A': (4.5, 2.8), 'R1': (3.5, 1.25), 'B': (8.5, 5.2), 'hole': (8.5, 6.3),
                  'C': (11.5, 2.6), 'R2': (10.4, 1.25), 'D': (2.5, 5.5), 'R3': (2.2, 6.9)}.items():
    ax.text(x, y, t, ha='center', va='center', fontsize=8 if len(t) > 3 else 9, weight='bold', color='#222')
ax.add_patch(Rectangle((6.0, 3.5), 0.5, 0.5, fill=False, ec='#8a4b00', ls='--', lw=1.3))
ax.annotate('low debris\n(only with --debris,\ninvisible to LiDAR)', (6.25, 3.5), (6.0, 2.3), fontsize=7, color='#8a4b00', ha='center', bbox=dict(fc='white', ec='#8a4b00', boxstyle='round,pad=0.25'), arrowprops=dict(arrowstyle='->', color='#8a4b00'))
ax.set_title('Simulated building (14 m x 8 m, 0.25 m cells) - layout only, no run results', fontsize=9)
fig.tight_layout(); fig.savefig('/home/claude/handover/fig/building.png', dpi=170); plt.close(fig)
print('figs ok')
