import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

GREY, GREEN, RED = '#eeeeee', '#d9ead3', '#b00020'
def box(ax, x, y, w, h, text, fc=GREY, ec='#333', fs=8.5, bold=True, ls='-'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.12', fc=fc, ec=ec, lw=1.2, ls=ls))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs, weight='bold' if bold else 'normal')
def arrow(ax, p, q, color='#222', rad=0.0, ls='-'):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=11, lw=1.3, color=color, ls=ls, connectionstyle=f'arc3,rad={rad}'))
def lab(ax, x, y, t, fs=7, ha='center', color='#222'):
    ax.text(x, y, t, ha=ha, va='center', fontsize=fs, color=color)

# ------------------------------------------------------------ state flow
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.set_xlim(0, 16.4); ax.set_ylim(0, 8.4); ax.axis('off')
W, H = 2.1, 1.0
P = {'BRIEFED': (0.3, 6.2), 'ENTER': (3.7, 6.2), 'LISTEN': (7.1, 6.2), 'TRUST-CHECK': (10.5, 6.2), 'FOLLOW': (13.9, 6.2),
     'LOCAL SEARCH': (7.1, 2.7), 'ACT': (13.9, 2.7), 'EXIT': (10.5, 0.8), 'SAFE_STOP': (0.3, 1.2)}
for n, (x, y) in P.items():
    box(ax, x, y, W, H, n, '#f8d7da' if n == 'SAFE_STOP' else GREY, fs=8 if len(n) > 9 else 8.5)
yy = 6.7
for a_, b_, t in [('BRIEFED', 'ENTER', 'briefing\nreceived'), ('ENTER', 'LISTEN', 'inside\nthe door'),
                  ('LISTEN', 'TRUST-CHECK', 'beacon\nheard'), ('TRUST-CHECK', 'FOLLOW', 'usable')]:
    x0, x1 = P[a_][0] + W, P[b_][0]
    arrow(ax, (x0, yy), (x1, yy)); lab(ax, (x0 + x1) / 2, yy + 0.55, t, 6.6)
# suspect: back to LISTEN, below the row
arrow(ax, (11.2, 6.2), (9.0, 6.2), rad=-0.45, color=RED)
lab(ax, 10.1, 5.05, 'suspect:\nflag + discard', 6.6, color=RED)
# follow -> listen over the top
ax.add_patch(FancyArrowPatch((14.6, 7.2), (8.0, 7.2), arrowstyle='-|>', mutation_scale=11, lw=1.3, color='#444', connectionstyle='arc3,rad=0.22'))
lab(ax, 11.3, 8.05, 'next beacon in the chain', 6.8, color='#444')
# follow -> act
arrow(ax, (14.95, 6.2), (14.95, 3.7)); lab(ax, 15.15, 4.95, 'target\nreached', 6.6, ha='left')
# listen <-> search
arrow(ax, (7.7, 6.2), (7.7, 3.7)); lab(ax, 7.5, 4.95, 'nothing heard /\nchain broken', 6.6, ha='right')
arrow(ax, (8.5, 3.7), (8.5, 6.2)); lab(ax, 8.65, 4.15, 'found one', 6.6, ha='left')
# exits
arrow(ax, (14.2, 2.7), (12.6, 1.5)); lab(ax, 14.0, 1.75, 'mission done\nor aborted', 6.6, ha='left')
arrow(ax, (9.0, 2.7), (10.5, 1.5)); lab(ax, 8.9, 1.75, 'gives up', 6.6, ha='right')
# safe stop
box(ax, 0.3, 3.4, W, 0.9, 'ANY STATE', '#ffffff', fs=8.5, ls='--')
arrow(ax, (1.35, 3.4), (1.35, 2.2), color=RED); lab(ax, 2.6, 2.8, 'tip-over, e-stop,\nunrecoverable fault', 6.6, ha='left', color=RED)
ax.text(0.3, 0.15, 'EXIT = leave through the entrance by retracing its own path. Whether the Executor must come back out is not specified in the documents (OPEN).',
        fontsize=7.2, style='italic')
fig.tight_layout(); fig.savefig('/home/claude/execpdf/exec_states.png', dpi=170); plt.close(fig)

# ------------------------------------------------------------ trust timeline
fig, ax = plt.subplots(figsize=(10, 3.7))
ax.set_xlim(0, 60); ax.set_ylim(-3.2, 4.4); ax.axis('off')
bands = [(0, 5, '#cfe8cf', 'FRESH'), (5, 30, '#fbe7b5', 'AGING'), (30, 60, '#f3c6c0', 'STALE')]
for a, b, col, name in bands:
    ax.add_patch(Rectangle((a, 0.6), b - a, 1.4, fc=col, ec='#555', lw=1))
    ax.text((a + b) / 2, 1.3, name, ha='center', va='center', fontsize=9, weight='bold')
ax.annotate('', xy=(60, 0.2), xytext=(0, 0.2), arrowprops=dict(arrowstyle='-|>', lw=1.2))
for t in range(0, 61, 10):
    ax.plot([t, t], [0.1, 0.3], color='#222'); ax.text(t, -0.25, f'{t}', ha='center', fontsize=7.5)
ax.text(30, -0.8, 'beacon age (minutes since it was written)', ha='center', fontsize=8)
for t, txt in [(2, '2 min'), (15, '15 min'), (40, '40 min')]:
    ax.plot([t], [2.7], marker='v', color='#1f4e79', ms=9)
    ax.text(t, 3.15, f'slide example\n{txt}', ha='center', fontsize=7.2, color='#1f4e79')
ax.text(2.5, 3.9, 'OFFICIAL (slide 2): examples shown for the same beacon at different ages', fontsize=7.4, color='#1f4e79', weight='bold')
ax.text(0.2, -1.55, 'Band boundaries at 5 and 30 min are the AI’s ASSUMPTION (not official). Real values are OPEN.', fontsize=7.6, color='#b45f06')
ax.add_patch(Rectangle((0, -3.0), 60, 1.0, fc='#f8d7da', ec=RED, lw=1.2, ls='--'))
ax.text(30, -2.5, 'SUSPECT = at ANY age: the Executor’s own live sensor contradicts the beacon  →  flag it and discard it', ha='center', va='center', fontsize=8, color=RED, weight='bold')
fig.tight_layout(); fig.savefig('/home/claude/execpdf/trust_timeline.png', dpi=170); plt.close(fig)
print('ok')
